#!/bin/bash

# Aristotle API セットアップスクリプト
# 1Password に置いた鍵を .env.tpl の参照で解決し、.env を作る。
# 鍵そのものはこのファイルにもリポジトリにも書かない。

set -e

ENV_FILE=".env"
TPL_FILE=".env.tpl"

echo "Aristotle API セットアップを開始します..."

command -v op >/dev/null 2>&1 || { echo "1Password CLI (op) が無い: brew install 1password-cli" >&2; exit 1; }
[ -f "$TPL_FILE" ] || { echo "$TPL_FILE が無い" >&2; exit 1; }

# .env ファイルが既に存在するか確認
if [ -f "$ENV_FILE" ]; then
    echo "警告: $ENV_FILE は既に存在します。"
    read -p "上書きしますか？ (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "セットアップをキャンセルしました。"
        exit 0
    fi
fi

# 1Password の参照 (op://dev/LeanResearch/ARISTOTLE_API_KEY) を実体に置き換える
op inject -i "$TPL_FILE" -o "$ENV_FILE" -f

# ファイルの権限を制限（所有者のみ読み書き可能）
chmod 600 "$ENV_FILE"

echo "✓ $ENV_FILE を作成しました"
echo "✓ ファイルの権限を設定しました（600: 所有者のみ読み書き可能）"
echo ""
echo "次のステップ:"
echo "  1. Pythonパッケージをインストール: pip install -r requirements.txt"
echo "  2. API接続をテスト: python aristotle_api.py"
echo ""
echo "注意: .envファイルは.gitignoreに含まれているため、Gitにコミットされません。"
