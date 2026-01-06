#!/usr/bin/env python3
"""
Aristotle API連携スクリプト
APIキーは.envファイルから読み込みます。
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any
import requests
from dotenv import load_dotenv

# .envファイルを読み込む
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# API設定
ARISTOTLE_API_KEY = os.getenv('ARISTOTLE_API_KEY')
ARISTOTLE_API_BASE_URL = 'https://api.aristotle.ai'  # 実際のURLに置き換えてください


class AristotleAPI:
    """Aristotle APIクライアント"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: APIキー。Noneの場合は環境変数から読み込みます。
        """
        self.api_key = api_key or ARISTOTLE_API_KEY
        if not self.api_key:
            raise ValueError(
                "APIキーが設定されていません。"
                ".envファイルにARISTOTLE_API_KEYを設定するか、"
                "環境変数として設定してください。"
            )
        self.base_url = ARISTOTLE_API_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        APIリクエストを送信
        
        Args:
            method: HTTPメソッド (GET, POST, etc.)
            endpoint: APIエンドポイント
            data: リクエストボディ
            params: クエリパラメータ
            
        Returns:
            APIレスポンス
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"APIリクエストエラー: {e}", file=sys.stderr)
            if hasattr(e.response, 'text'):
                print(f"レスポンス: {e.response.text}", file=sys.stderr)
            raise
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GETリクエスト"""
        return self._request('GET', endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """POSTリクエスト"""
        return self._request('POST', endpoint, data=data)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """PUTリクエスト"""
        return self._request('PUT', endpoint, data=data)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """DELETEリクエスト"""
        return self._request('DELETE', endpoint)


def main():
    """メイン関数 - 使用例"""
    try:
        api = AristotleAPI()
        print("✓ Aristotle APIクライアントが正常に初期化されました")
        print(f"APIキー: {api.api_key[:10]}...")
        
        # ここに実際のAPI呼び出しを追加
        # 例:
        # result = api.get('/v1/endpoint')
        # print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

