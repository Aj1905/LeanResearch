# .env の雛形。秘密の値は 1Password に置き、ここには参照だけを書く (push してよい)。
# 実体を作る:  op inject -i .env.tpl -o .env   (setup_api.sh が同じことをする)
# 初回登録 (手元の .env から):  env-to-op LeanResearch

# Aristotle API Configuration
ARISTOTLE_API_KEY=op://dev/LeanResearch/ARISTOTLE_API_KEY
