#!/usr/bin/env python3
"""
Aristotle CLI ラッパースクリプト

実現したい用途:
- Leanファイルに sorry を置いて、その場所の証明を完成させる
  - sorryを全て編集する
    このスクリプトは --target で「N番目の sorry だけ残す」一時ファイル生成を提供する。
- sorry 付近（定理ヘッダ doc-comment）に自然言語の証明スケッチを書いて誘導する
  - Aristotle の Lean mode 機能（PROVIDED SOLUTION: タグ）をそのまま使う。
- CLI引数で aristotle に渡すファイル名を指定する

使い方:
  python3 aristotle_runner.py fill-sorry --input path/to/theorem.lean --output solution.lean
  python3 aristotle_runner.py fill-sorry --input path/to/theorem.lean --target 1 --output solution.lean
  python3 aristotle_runner.py formalize --input path/to/problem.txt --output solution.lean
  python3 aristotle_runner.py tui
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

from dotenv import load_dotenv

ENV_FILE_NAME = ".env"
ENV_KEY_NAME = "ARISTOTLE_API_KEY"
CLI_COMMAND = "aristotle"


# -------------------------
# Data / errors
# -------------------------
@dataclass(frozen=True)
class CliResult:
    returncode: int


class AristotleCliError(RuntimeError):
    pass


# -------------------------
# Env / IO helpers
# -------------------------
def load_api_key_from_env(script_dir: Path) -> str:
    env_path = script_dir / ENV_FILE_NAME
    load_dotenv(dotenv_path=env_path)

    api_key = os.getenv(ENV_KEY_NAME)
    if not api_key:
        raise ValueError(
            f"APIキーが設定されていません。{env_path} に {ENV_KEY_NAME}=... を設定してください。"
        )
    return api_key


def require_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"入力ファイルが見つかりません: {path}")
    if not path.is_file():
        raise ValueError(f"ファイルではありません: {path}")


def mask_key(api_key: str) -> str:
    return api_key[:8] + "..."


# -------------------------
# Lean-aware minimal parser
# -------------------------
class LeanScanner:
    """
    Lean のコメント/文字列をざっくり避けて token を扱うための超軽量スキャナ。

    対応:
    - line comment: -- ... \n
    - block comment: /- ... -/ (ネストは近似的に 1 段)
    - string: "..." (バックスラッシュエスケープ対応)

    目的:
    - コメントや文字列中の `sorry` を誤置換しない
    """

    def __init__(self, text: str) -> None:
        self.text = text
        self.n = len(text)

    @staticmethod
    def _is_ident_char(ch: str) -> bool:
        return ch.isalnum() or ch == "_"

    def replace_sorry_except_nth(self, keep_index_1based: int) -> tuple[str, int]:
        """
        コメント/文字列を避けつつ、トークンとしての `sorry` を数える。
        keep_index_1based 番目の `sorry` だけ残し、他は `admit` に置換する。

        Returns:
          (new_text, total_sorry_count)
        """
        if keep_index_1based <= 0:
            raise ValueError("--target は 1 以上を指定してください。")

        s = self.text
        out: list[str] = []

        i = 0
        sorry_count = 0

        in_line_comment = False
        in_block_comment = False
        in_string = False

        while i < self.n:
            ch = s[i]

            # line comment end
            if in_line_comment:
                out.append(ch)
                if ch == "\n":
                    in_line_comment = False
                i += 1
                continue

            # block comment end
            if in_block_comment:
                if i + 1 < self.n and s[i : i + 2] == "-/":
                    out.append("-/")
                    i += 2
                    in_block_comment = False
                else:
                    out.append(ch)
                    i += 1
                continue

            # string end / escape
            if in_string:
                out.append(ch)
                if ch == "\\" and i + 1 < self.n:
                    out.append(s[i + 1])
                    i += 2
                    continue
                if ch == '"':
                    in_string = False
                i += 1
                continue

            # comment starts
            if i + 1 < self.n and s[i : i + 2] == "--":
                out.append("--")
                i += 2
                in_line_comment = True
                continue

            if i + 1 < self.n and s[i : i + 2] == "/-":
                out.append("/-")
                i += 2
                in_block_comment = True
                continue

            # string start
            if ch == '"':
                out.append('"')
                i += 1
                in_string = True
                continue

            # token scan for 'sorry'
            if ch == "s" and i + 4 < self.n and s[i : i + 5] == "sorry":
                prev_ok = (i == 0) or (not self._is_ident_char(s[i - 1]))
                next_ok = (i + 5 == self.n) or (not self._is_ident_char(s[i + 5]))
                if prev_ok and next_ok:
                    sorry_count += 1
                    if sorry_count == keep_index_1based:
                        out.append("sorry")
                    else:
                        out.append("admit")
                    i += 5
                    continue

            # default
            out.append(ch)
            i += 1

        return ("".join(out), sorry_count)


def create_temp_targeted_lean(input_path: Path, target_sorry_index: int) -> tuple[Path, int]:
    """
    input_path を読み込み、target_sorry_index番目の sorry だけ残し他は admit に置換した
    一時ファイルを作る。
    """
    text = input_path.read_text(encoding="utf-8")
    scanner = LeanScanner(text)
    replaced, total = scanner.replace_sorry_except_nth(target_sorry_index)

    if total == 0:
        raise ValueError("このファイルには（コメント/文字列外の）`sorry` が見つかりませんでした。")
    if target_sorry_index > total:
        raise ValueError(f"--target {target_sorry_index} は範囲外です。sorry は {total} 個あります。")

    tmp_dir = Path(tempfile.mkdtemp(prefix="aristotle_target_"))
    tmp_path = tmp_dir / input_path.name
    tmp_path.write_text(replaced, encoding="utf-8")
    return tmp_path, total


# -------------------------
# CLI runner
# -------------------------
def run_cli_streaming(args: Sequence[str], api_key: str, cwd: Optional[Path] = None) -> CliResult:
    """
    stdout/stderr をそのままターミナルに流す（TUIや進捗表示向け）
    """
    env = os.environ.copy()
    env[ENV_KEY_NAME] = api_key

    try:
        cp = subprocess.run(
            [CLI_COMMAND, *args],
            cwd=str(cwd) if cwd else None,
            env=env,
            check=False,
        )
        return CliResult(returncode=cp.returncode)
    except FileNotFoundError as e:
        raise AristotleCliError(
            "aristotle コマンドが見つかりません。まず `pip install aristotlelib` を実行してください。"
        ) from e


def run_cli_captured(args: Sequence[str], api_key: str, cwd: Optional[Path] = None) -> tuple[int, str, str]:
    """
    stdout/stderr を回収（失敗時に出しやすい）
    """
    env = os.environ.copy()
    env[ENV_KEY_NAME] = api_key

    try:
        cp = subprocess.run(
            [CLI_COMMAND, *args],
            cwd=str(cwd) if cwd else None,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        return cp.returncode, cp.stdout, cp.stderr
    except FileNotFoundError as e:
        raise AristotleCliError(
            "aristotle コマンドが見つかりません。まず `pip install aristotlelib` を実行してください。"
        ) from e


# -------------------------
# Main
# -------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Aristotle CLI wrapper (enhanced)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_fill = sub.add_parser("fill-sorry", help="Leanファイルを投げて sorry を埋める（prove-from-file）")
    p_fill.add_argument("--input", type=Path, required=True, help="Leanファイルパス")
    p_fill.add_argument("--output", type=Path, required=False, help="出力先 .lean（任意）")
    p_fill.add_argument(
        "--target",
        type=int,
        required=False,
        help="N番目の sorry だけ埋めたいときに指定（他の sorry は admit にして一時ファイルを投げる）",
    )

    p_formalize = sub.add_parser("formalize", help="自然言語（txt等）を形式化（--informal）")
    p_formalize.add_argument("--input", type=Path, required=True, help="自然言語のファイルパス")
    p_formalize.add_argument("--output", type=Path, required=False, help="出力先 .lean（任意）")
    p_formalize.add_argument(
        "--formal-context",
        type=Path,
        required=False,
        help="非形式入力に対するLean側の文脈（--formal-input-context に渡す）",
    )

    sub.add_parser("tui", help="TUIを開く（対話で質問・探索）")

    return parser


def main(argv: list[str]) -> int:
    script_dir = Path(__file__).resolve().parent
    api_key = load_api_key_from_env(script_dir)

    parser = build_parser()
    args = parser.parse_args(argv)

    print(f"✓ APIキー読み込みOK: {mask_key(api_key)}")

    if args.command == "fill-sorry":
        require_file(args.input)

        input_path: Path = args.input
        temp_path: Optional[Path] = None

        if args.target is not None:
            temp_path, total = create_temp_targeted_lean(input_path, args.target)
            print(f"✓ sorry は合計 {total} 個。--target={args.target} 以外は admit にして投げます。")
            input_path = temp_path

        cli_args: list[str] = ["prove-from-file", str(input_path)]
        if args.output:
            cli_args += ["--output-file", str(args.output)]

        code, out, err = run_cli_captured(cli_args, api_key=api_key, cwd=script_dir)
        if code != 0:
            print(err, file=sys.stderr)
            return code
        print(out)
        return 0

    if args.command == "formalize":
        require_file(args.input)

        cli_args = ["prove-from-file", str(args.input), "--informal"]
        if args.formal_context:
            require_file(args.formal_context)
            cli_args += ["--formal-input-context", str(args.formal_context)]
        if args.output:
            cli_args += ["--output-file", str(args.output)]

        code, out, err = run_cli_captured(cli_args, api_key=api_key, cwd=script_dir)
        if code != 0:
            print(err, file=sys.stderr)
            return code
        print(out)
        return 0

    if args.command == "tui":
        # TUIは capture しない（画面が出なくなるため）
        result = run_cli_streaming([], api_key=api_key, cwd=script_dir)
        return result.returncode

    raise RuntimeError("Unknown command reached (should be impossible).")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
