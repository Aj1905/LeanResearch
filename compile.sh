#!/bin/bash

# LeanResearch用: TeXファイルをコンパイルしてPDFを生成し、自動的に開くスクリプト
# 使用方法: ./compile.sh [texファイル名]
# デフォルト: graduation_paper.tex

TEX_FILE="${1:-graduation_paper.tex}"
BASE_NAME="${TEX_FILE%.tex}"
BUILD_DIR="build"
PDF_FILE="${BASE_NAME}.pdf"

# buildディレクトリを作成
mkdir -p "$BUILD_DIR"

# ファイルの存在確認
if [ ! -f "$TEX_FILE" ]; then
    echo "エラー: ファイル '$TEX_FILE' が見つかりません。"
    exit 1
fi

# uplatexを使用（graduation_paper.texはuplatex指定）
echo "コンパイラ: uplatex"
echo "コンパイル中: $TEX_FILE"
echo "中間ファイルは $BUILD_DIR/ に出力されます"

# uplatexで2回コンパイル + dvipdfmx
uplatex -interaction=nonstopmode -output-directory="$BUILD_DIR" "$TEX_FILE" || exit 1
uplatex -interaction=nonstopmode -output-directory="$BUILD_DIR" "$TEX_FILE" || exit 1
dvipdfmx -o "$PDF_FILE" "$BUILD_DIR/${BASE_NAME}.dvi" || exit 1

# PDFファイルの存在確認
if [ -f "$PDF_FILE" ]; then
    echo "✓ PDF生成成功: $PDF_FILE"
    # macOSでPDFを開く
    open "$PDF_FILE"
    echo "PDFを開きました。"
else
    echo "エラー: PDFファイルが生成されませんでした。"
    exit 1
fi

