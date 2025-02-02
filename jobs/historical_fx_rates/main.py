import os
import time
import requests
from google.cloud import pubsub_v1

# API キーを環境変数から取得します
api_key = os.environ.get('FINANCIAL_MODELING_PREP_API_KEY')

# Pub/Sub トピック ID を取得します
topic_id = os.environ.get('HISTORICAL_FX_RATES_TOPIC_ID')

def get_historical_fx_data(timeframe):
    """
    Financial Modeling Prep API から過去の為替レートデータを取得し、Pub/Sub に送信する関数
    """
    # Financial Modeling Prep API のエンドポイント URL を設定します
    url = f"https://financialmodelingprep.com/api/v3/historical-chart/{timeframe}/USDJPY?apikey={api_key}"

    try:
        # API リクエストを送信します
        response = requests.get(url)
        response.raise_for_status()  # エラーレスポンスの場合、例外を発生させます

        # レスポンスデータを JSON 形式で取得します
        data = response.json()

        # Pub/Sub メッセージを送信します
        publish_message(topic_id, data)

        print(f"{timeframe} の過去の為替レートデータを Pub/Sub に送信しました。")

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
    # 1日1回、午前0時にデータを取得
    while True:
        now = time.localtime()
        if now.tm_hour == 0 and now.tm_min == 0:
            for timeframe in ["1day", "1week", "1month"]:
                get_historical_fx_data(timeframe)
        time.sleep(60)  # 1分ごとに実行

if __name__ == "__main__":
    main()