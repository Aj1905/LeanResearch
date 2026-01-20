# LeanResearch用: TeXファイルをコンパイルするMakefile
# 使用方法: make または make pdf

BUILD_DIR = build
TEX_FILE  = graduation_paper.tex
PDF_FILE  = graduation_paper.pdf

.PHONY: all pdf clean help $(BUILD_DIR)

# buildディレクトリを作成
$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

# デフォルトターゲット
.DEFAULT_GOAL := all

all: $(PDF_FILE)
	@echo "✓ 完了"

pdf: $(PDF_FILE)
	@echo "✓ 完了"

# graduation_paper.tex からPDFを生成（LuaLaTeX使用）
# -output-directory で中間ファイルを build/ に固定し、参照・目次を安定させる
# -halt-on-error で壊れたPDFの生成を防ぎ、原因をログに出す
$(PDF_FILE): $(TEX_FILE) | $(BUILD_DIR)
	@echo "コンパイル中: $(TEX_FILE)"
	@echo "使用コンパイラ: lualatex"
	@echo "中間ファイルは $(BUILD_DIR)/ に出力されます"
	lualatex -halt-on-error -file-line-error -interaction=nonstopmode -output-directory=$(BUILD_DIR) $(TEX_FILE)
	lualatex -halt-on-error -file-line-error -interaction=nonstopmode -output-directory=$(BUILD_DIR) $(TEX_FILE)
	lualatex -halt-on-error -file-line-error -interaction=nonstopmode -output-directory=$(BUILD_DIR) $(TEX_FILE)
	@cp -f $(BUILD_DIR)/$(PDF_FILE) .
	@if [ -f "$(PDF_FILE)" ]; then \
		echo "✓ PDF生成成功: $(PDF_FILE)"; \
		open "$(PDF_FILE)"; \
	else \
		echo "エラー: PDFファイルが生成されませんでした。"; \
		exit 1; \
	fi

# 中間ファイルを削除
clean:
	@echo "中間ファイルを削除中..."
	@rm -rf $(BUILD_DIR)
	@rm -f $(PDF_FILE)
	@echo "✓ 削除完了"

# ヘルプ表示
help:
	@echo "使用方法:"
	@echo "  make        - $(TEX_FILE) をコンパイルしてPDFを開く"
	@echo "  make pdf    - 同上"
	@echo "  make clean  - 中間ファイルとbuildディレクトリを削除"
	@echo ""
	@echo "中間ファイルは $(BUILD_DIR)/ ディレクトリに出力されます"
