# lambda/index.py
import json
import os
import boto3
import re  # 正規表現モジュールをインポート
from botocore.exceptions import ClientError
import urllib.request



# Lambda コンテキストからリージョンを抽出する関数
def extract_region_from_arn(arn):
    # ARN 形式: arn:aws:lambda:region:account-id:function:function-name
    match = re.search('arn:aws:lambda:([^:]+):', arn)
    if match:
        return match.group(1)
    return "us-east-1"  # デフォルト値

# グローバル変数としてクライアントを初期化（初期値）
bedrock_client = None

# モデルID
MODEL_ID = os.environ.get("MODEL_ID", "us.amazon.nova-lite-v1:0")

def lambda_handler(event, context):
    # FastAPIのエンドポイントURL
    url = "https://5b95-34-125-180-161.ngrok-free.app/generate"  # ← ここをあなたのngrok公開URLに！

    # ユーザーから受け取ったメッセージを取得
    prompt = event["messages"][0]["content"]

    # FastAPI に送るリクエストデータ
    data = {
        "prompt": prompt,
        "max_new_tokens": 512,
        "do_sample": True,
        "temperature": 0.7,
        "top_p": 0.9
    }

    # HTTP POSTリクエスト送信
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            reply = result.get("generated_text", "応答が取得できませんでした。")

            return {
                "statusCode": 200,
                "body": json.dumps({
                    "reply": reply
                })
            }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }