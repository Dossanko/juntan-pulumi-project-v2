import os
import time
import requests
from google.cloud import pubsub_v1

# API キーを環境変数から取得します
api_key = os.environ.get('FINANCIAL_MODELING_PREP_API_KEY')

# Pub/Sub トピック ID を取得します
topic_id = os.environ.get('FX_RATES_TOPIC_ID')

def get_fx_data(currency_pair):
    """
    Financial Modeling Prep API から為替レートデータを取得し、Pub/Sub に送信する関数
    """
    # Financial Modeling Prep API のエンドポイント URL を設定します
    url = f"https://financialmodelingprep.com/api/v3/forex/{currency_pair}?apikey={api_key}"

    try:
        # API リクエストを送信します
        response = requests.get(url)
        response.raise_for_status()  # エラーレスポンスの場合、例外を発生させます

        # レスポンスデータを JSON 形式で取得します
        data = response.json()

        # Pub/Sub メッセージを送信します
        publish_message(topic_id, data)

        print(f"{currency_pair} の為替レートデータを Pub/Sub に送信しました。")

    except requests.exceptions.RequestException as e:
        print(f"API リクエストエラー: {e}")
    except Exception as e:
        print(f"エラー: {e}")

def publish_message(topic_id, data):
    """
    Pub/Sub メッセージを送信する関数
    """
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(os.environ.get('GCP_PROJECT'), topic_id)

    # データを JSON 形式にエンコードします
    message_data = json.dumps(data).encode("utf-8")

    # Pub/Sub メッセージを送信します
    future = publisher.publish(topic_path, message_data)
    print(f"Published message ID: {future.result()}")

def main():
    # 1時間ごとにデータを取得
    while True:
        for currency_pair in ["EURUSD", "GBPJPY", "GBPUSD", "EURJPY"]:
            get_fx_data(currency_pair)
        time.sleep(3600)  # 1時間(3600秒)ごとに実行

if __name__ == "__main__":
    main()