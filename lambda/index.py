#!/usr/bin/env python3
import json
import os
import re
import urllib.request
import urllib.error

# 環境変数からエンドポイントを取得
API_URL = os.environ.get("https://5653-35-233-187-88.ngrok-free.app/")
if not API_URL:
    raise RuntimeError("Environment variable COLAB_API_URL is not set")

def lambda_handler(event, context):
    try:
        # リクエストボディの解析
        body = json.loads(event.get('body', '{}'))
        message = body.get('message', '')
        conversation_history = body.get('conversationHistory', [])

        # FastAPI 側に投げる payload
        payload = {
            "message": message,
            "conversationHistory": conversation_history
        }
        data = json.dumps(payload).encode('utf-8')

        req = urllib.request.Request(
            API_URL,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        # FastAPI サーバーへ POST
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp_body = resp.read().decode('utf-8')
            result = json.loads(resp_body)

        # レスポンスからアシスタント応答と履歴を取得
        assistant_response = result.get('response', '')
        new_history = result.get('conversationHistory', conversation_history)

        # 成功レスポンスを返却
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": new_history
            })
        }

    except urllib.error.HTTPError as e:
        # HTTP エラー時
        err_body = e.read().decode('utf-8')
        print(f"HTTPError {e.code}: {err_body}")
        return {
            "statusCode": e.code,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"success": False, "error": err_body})
        }

    except Exception as e:
        # その他例外
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"success": False, "error": str(e)})
        }
