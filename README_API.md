# Aristotle API連携ガイド

## セットアップ

### 1. Aristotle CLIのインストール

pipxを使用してインストールします：

```bash
# pipxをインストール（初回のみ）
brew install pipx

# pipxのパスを設定（初回のみ、シェルの設定ファイルに追加）
pipx ensurepath

# aristotlelibをインストール
pipx install aristotlelib
```

**注意**: 新しいターミナルを開くか、`source ~/.zshrc`（または`source ~/.bashrc`）を実行して、`pipx ensurepath`の変更を反映してください。

### 2. Pythonパッケージのインストール

その他の依存パッケージをインストールします：

```bash
pip3 install --user --break-system-packages -r requirements.txt
```

**注意**: Python 3.13以降では、`externally-managed-environment`エラーを回避するために`--break-system-packages`フラグが必要です。このフラグはシステムのPython環境保護を無効化しますが、`--user`フラグと併用することで、ユーザー領域にインストールされます。

### 3. APIキーの設定

セットアップスクリプトを実行して`.env`ファイルを作成します：

```bash
./setup_api.sh
```

必要に応じて、環境変数としても設定できます：

```bash
export ARISTOTLE_API_KEY=arstl_BbL7ymjn_Sl8Wx4Eey3QCT4bGLrawbIZyeTG5cEQ-Z8
```

## 使用方法

`aristotle_api.py`は、Aristotle CLIのラッパースクリプトです。公式CLI/SDKの仕様に追従するため、壊れにくい設計になっています。

### 1. sorry補填（Leanファイルを投げる）

Leanファイル内の`sorry`を自動で埋めます：

```bash
python aristotle_api.py fill-sorry --input path/to/theorem.lean --output solution.lean
```

**例:**
```bash
# PrFiles/Ceva.leanのsorryを埋める
python aristotle_api.py fill-sorry --input PrFiles/Ceva.lean --output PrFiles/Ceva_filled.lean
```

### 2. 自然言語証明の形式化

自然言語で書かれた証明（txt等）をLean形式に変換します：

```bash
python aristotle_api.py formalize --input path/to/problem.txt --output solution.lean
```

**例:**
```bash
# 自然言語証明を形式化
python aristotle_api.py formalize --input proof.txt --output formalized_proof.lean
```

### 3. TUI（対話型インターフェース）

対話形式で質問や探索を行います：

```bash
python aristotle_api.py tui
```

**注意**: TUIモードは現在`capture_output`で実行されているため、実際の対話には制限があります。実運用では別実装を検討してください。

### コマンドライン引数の詳細

- `fill-sorry`: Leanファイルを投げてsorryを埋める（`prove-from-file`コマンドを使用）
  - `--input`: 入力Leanファイルパス（必須）
  - `--output`: 出力先.leanファイルパス（任意）

- `formalize`: 自然言語（txt等）を形式化（`--informal`フラグ付きで`prove-from-file`を使用）
  - `--input`: 自然言語証明のファイルパス（必須）
  - `--output`: 出力先.leanファイルパス（任意）

- `tui`: TUIを開く（対話で質問・探索）

## アーキテクチャ

このスクリプトは以下の設計思想に基づいています：

- **公式CLI/SDKの使用**: REST APIを直接実装せず、公式の`aristotle` CLIコマンドをsubprocess経由で実行します
- **壊れにくい設計**: 公式の仕様変更に追従しやすく、メンテナンスが容易です
- **環境変数の注入**: APIキーは環境変数として`aristotle` CLIに渡されます

## セキュリティ

- 本番環境では、環境変数やシークレット管理サービスを使用してください

## トラブルシューティング

### `aristotle`コマンドが見つからないエラー

```
AristotleCliError: aristotle コマンドが見つかりません。まず `pip install aristotlelib` を実行してください。
```

**解決方法:**
```bash
# pipxを使用してインストール
brew install pipx
pipx ensurepath
pipx install aristotlelib

# 新しいターミナルを開くか、以下を実行
source ~/.zshrc  # または source ~/.bashrc
```

### APIキーが見つからないエラー

```
ValueError: APIキーが設定されていません。.env に ARISTOTLE_API_KEY=... を設定してください。
```

**解決方法:**
1. `.env`ファイルが存在することを確認
2. `.env`ファイルに`ARISTOTLE_API_KEY`が設定されていることを確認
3. 環境変数として設定されている場合は、`echo $ARISTOTLE_API_KEY`で確認

### 入力ファイルが見つからないエラー

```
FileNotFoundError: 入力ファイルが見つかりません: path/to/file.lean
```

**解決方法:**
- `--input`で指定したファイルパスが正しいか確認
- ファイルが存在するか確認
- 相対パスと絶対パスの違いに注意

**解決方法: pipxを使用（推奨）**

```bash
# pipxをインストール
brew install pipx
pipx ensurepath

# aristotlelibをインストール
pipx install aristotlelib

# 新しいターミナルを開くか、以下を実行
source ~/.zshrc  # または source ~/.bashrc
```

**別の方法: --userフラグと--break-system-packagesフラグを使用**

```bash
# Python 3.13以降では --break-system-packages が必要
pip3 install --user --break-system-packages aristotlelib
pip3 install --user --break-system-packages -r requirements.txt
```

### `pip`コマンドが見つからないエラー

macOSでは、`pip`の代わりに`pip3`を使用してください：

```bash
# エラー: zsh: command not found: pip
# 解決方法: pipxを使用（推奨）
brew install pipx
pipx install aristotlelib

# または、pip3を使用（--break-system-packagesフラグが必要）
pip3 install --user --break-system-packages -r requirements.txt
```

### その他のエラー

- `aristotle` CLIのエラーメッセージが`stderr`に出力されます

