#!/bin/bash

# Aristotle APIセットアップスクリプト
# このスクリプトは.envファイルを作成し、APIキーを設定します。

set -e

ENV_FILE=".env"
EXAMPLE_FILE=".env.example"
API_KEY="arstl_BbL7ymjn_Sl8Wx4Eey3QCT4bGLrawbIZyeTG5cEQ-Z8"

echo "Aristotle APIセットアップを開始します..."

# .envファイルが既に存在するか確認
if [ -f "$ENV_FILE" ]; then
    echo "警告: $ENV_FILE は既に存在します。"
    read -p "上書きしますか？ (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "セットアップをキャンセルしました。"
        exit 0
    fi
fi

# .envファイルを作成
cat > "$ENV_FILE" << EOF
# Aristotle API Configuration
# このファイルには機密情報が含まれています。Gitにコミットしないでください。
ARISTOTLE_API_KEY=$API_KEY
EOF

# ファイルの権限を制限（所有者のみ読み書き可能）
chmod 600 "$ENV_FILE"

echo "✓ $ENV_FILE を作成しました"
echo "✓ ファイルの権限を設定しました（600: 所有者のみ読み書き可能）"
echo ""
echo "次のステップ:"
echo "  1. Pythonパッケージをインストール: pip install -r requirements.txt"
echo "  2. API接続をテスト: python aristotle_api.py"
echo ""
echo "注意: .envファイルは既に.gitignoreに含まれているため、Gitにコミットされません。"


