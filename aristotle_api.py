#!/usr/bin/env python3
"""
Aristotle（Harmonic）CLI ラッパースクリプト

- .env から ARISTOTLE_API_KEY を読み込み
- `aristotle` CLI を subprocess 経由で実行する
- REST を自作せず、公式CLI/SDKの仕様に追従する（壊れにくい）

使い方例:
  # sorry補填（Leanファイルを投げる）
  python3 aristotle_runner.py fill-sorry --input path/to/theorem.lean --output solution.lean

  # 自然言語証明の形式化（txt等を --informal で投げる）
  python3 aristotle_runner.py formalize --input path/to/problem.txt --output solution.lean

  # TUI（質問や探索をしたい場合）
  python3 aristotle_runner.py tui
"""

from __future__ import annotations

import os
import sys
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence, Optional

from dotenv import load_dotenv


ENV_FILE_NAME = ".env"
ENV_KEY_NAME = "ARISTOTLE_API_KEY"
CLI_COMMAND = "aristotle"


@dataclass(frozen=True)
class CliResult:
    returncode: int
    stdout: str
    stderr: str


class AristotleCliError(RuntimeError):
    pass


def load_api_key_from_env(script_dir: Path) -> str:
    env_path = script_dir / ENV_FILE_NAME
    load_dotenv(dotenv_path=env_path)

    api_key = os.getenv(ENV_KEY_NAME)
    if not api_key:
        raise ValueError(
            f"APIキーが設定されていません。{env_path} に {ENV_KEY_NAME}=... を設定してください。"
        )
    return api_key


def run_cli(args: Sequence[str], api_key: str, cwd: Optional[Path] = None) -> CliResult:
    """
    aristotle CLI を実行する。APIキーは環境変数で注入する。

    NOTE: ここで stdout/stderr を両方回収して、失敗時に詳細を出す。
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
        return CliResult(returncode=cp.returncode, stdout=cp.stdout, stderr=cp.stderr)
    except FileNotFoundError as e:
        raise AristotleCliError(
            "aristotle コマンドが見つかりません。まず `pip install aristotlelib` を実行してください。"
        ) from e


def require_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"入力ファイルが見つかりません: {path}")
    if not path.is_file():
        raise ValueError(f"ファイルではありません: {path}")


def mask_key(api_key: str) -> str:
    return api_key[:8] + "..."


def main(argv: list[str]) -> int:
    script_dir = Path(__file__).resolve().parent
    api_key = load_api_key_from_env(script_dir)

    import argparse

    parser = argparse.ArgumentParser(description="Aristotle CLI wrapper")
    sub = parser.add_subparsers(dest="command", required=True)

    p_fill = sub.add_parser("fill-sorry", help="Leanファイルを投げて sorry を埋める（prove-from-file）")
    p_fill.add_argument("--input", type=Path, required=True, help="Leanファイルパス")
    p_fill.add_argument("--output", type=Path, required=False, help="出力先 .lean（任意）")

    p_formalize = sub.add_parser("formalize", help="自然言語（txt等）を形式化（--informal）")
    p_formalize.add_argument("--input", type=Path, required=True, help="自然言語証明のファイルパス")
    p_formalize.add_argument("--output", type=Path, required=False, help="出力先 .lean（任意）")

    p_tui = sub.add_parser("tui", help="TUIを開く（対話で質問・探索）")

    args = parser.parse_args(argv)

    print(f"✓ APIキー読み込みOK: {mask_key(api_key)}")

    if args.command == "fill-sorry":
        require_file(args.input)
        cli_args = ["prove-from-file", str(args.input)]
        if args.output:
            cli_args += ["--output-file", str(args.output)]

        result = run_cli(cli_args, api_key=api_key, cwd=script_dir)
        if result.returncode != 0:
            print(result.stderr, file=sys.stderr)
            return result.returncode
        print(result.stdout)
        return 0

    if args.command == "formalize":
        require_file(args.input)
        cli_args = ["prove-from-file", str(args.input), "--informal"]
        if args.output:
            cli_args += ["--output-file", str(args.output)]

        result = run_cli(cli_args, api_key=api_key, cwd=script_dir)
        if result.returncode != 0:
            print(result.stderr, file=sys.stderr)
            return result.returncode
        print(result.stdout)
        return 0

    if args.command == "tui":
        # `aristotle` を引数なしで起動（TUI）
        result = run_cli([], api_key=api_key, cwd=script_dir)
        # TUIは capture_output だと見えないので、実運用なら capture しない別実装にするのが普通。
        # ここでは「起動できる」確認用途として残す。
        if result.returncode != 0:
            print(result.stderr, file=sys.stderr)
            return result.returncode
        print(result.stdout)
        return 0

    raise RuntimeError("Unknown command reached (should be impossible).")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
