# Aristotle API連携ガイド

## セットアップ

### 1. Pythonパッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. APIキーの設定

セットアップスクリプトを実行して`.env`ファイルを作成します：

```bash
./setup_api.sh
```

または、手動で`.env`ファイルを作成することもできます：

```bash
# テンプレートからコピー
cp env.template .env

# .envファイルを編集してAPIキーを設定
# ARISTOTLE_API_KEY=arstl_BbL7ymjn_Sl8Wx4Eey3QCT4bGLrawbIZyeTG5cEQ-Z8
```

`.env`ファイルは`.gitignore`に含まれているため、Gitにコミットされません。

必要に応じて、環境変数としても設定できます：

```bash
export ARISTOTLE_API_KEY=arstl_BbL7ymjn_Sl8Wx4Eey3QCT4bGLrawbIZyeTG5cEQ-Z8
```

## 使用方法

### Lean 4から直接使用（推奨）

Lean 4プロジェクト内から直接APIを呼び出すことができます：

```lean
import PrFiles.AristotleAPI

-- API接続をテスト
#eval AristotleAPI.testConnection

-- GETリクエストの例
#eval do
  let result ← AristotleAPI.get "/v1/endpoint"
  IO.println result.pretty

-- POSTリクエストの例
#eval do
  let data := Json.mkObj [("key", "value")]
  let result ← AristotleAPI.post "/v1/endpoint" data
  IO.println result.pretty
```

**注意**: 環境変数`ARISTOTLE_API_KEY`が設定されている必要があります：
```bash
export ARISTOTLE_API_KEY=arstl_BbL7ymjn_Sl8Wx4Eey3QCT4bGLrawbIZyeTG5cEQ-Z8
```

### Pythonスクリプトから使用

```python
from aristotle_api import AristotleAPI

# APIクライアントを初期化
api = AristotleAPI()

# GETリクエストの例
result = api.get('/v1/endpoint')

# POSTリクエストの例
data = {'key': 'value'}
result = api.post('/v1/endpoint', data=data)
```

### コマンドラインから使用

```bash
python aristotle_api.py
```

## セキュリティ

- **APIキーは絶対にGitにコミットしないでください**
- `.env`ファイルは既に`.gitignore`に含まれています
- 本番環境では、環境変数やシークレット管理サービスを使用してください

## APIエンドポイント

実際のAPIエンドポイントURLは以下のファイルで更新してください：
- Lean 4: `PrFiles/AristotleAPI.lean`の`baseUrl`
- Python: `aristotle_api.py`の`ARISTOTLE_API_BASE_URL`

現在の設定: `https://api.aristotle.ai`

## なぜ2つの実装があるのか？

- **Lean 4実装** (`PrFiles/AristotleAPI.lean`): Leanプロジェクト内から直接APIを呼び出せます。定理証明や形式化のワークフローに統合しやすいです。
- **Python実装** (`aristotle_api.py`): より柔軟で、豊富なライブラリを活用できます。スクリプトやツールとして使用する場合に便利です。

どちらを使用しても構いませんが、Lean研究プロジェクトでは**Lean 4実装を推奨**します。

## トラブルシューティング

### APIキーが見つからないエラー

1. `.env`ファイルが存在することを確認
2. `.env`ファイルに`ARISTOTLE_API_KEY`が設定されていることを確認
3. 環境変数として設定されている場合は、`echo $ARISTOTLE_API_KEY`で確認

### 接続エラー

1. インターネット接続を確認
2. APIのベースURLが正しいか確認
3. APIキーが有効か確認

