import os
import time
import requests
from google.cloud import pubsub_v1

# Yahoo! finance API のエンドポイント URL を設定します
yahoo_finance_urls = {
    "N225": "https://query1.finance.yahoo.com/v8/finance/chart/%5EN225?region=US&lang=en-US&includePrePost=false&interval=1m&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance",
    "DJI": "https://query1.finance.yahoo.com/v8/finance/chart/%5EDJI?region=US&lang=en-US&includePrePost=false&interval=1m&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance",
    "GSPC": "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?region=US&lang=en-US&includePrePost=false&interval=1m&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance",
}

# Pub/Sub トピック ID を取得します
topic_id = os.environ.get('STOCK_INDICES_TOPIC_ID')

def get_stock_index_data(index_name, url):
    """
    Yahoo! finance API から株価指数データを取得し、Pub/Sub に送信する関数
    """
    try:
        # API リクエストを送信します
        response = requests.get(url)
        response.raise_for_status()  # エラーレスポンスの場合、例外を発生させます

        # レスポンスデータを JSON 形式で取得します
        data = response.json()

        # Pub/Sub メッセージを送信します
        publish_message(topic_id, {index_name: data})

        print(f"{index_name} の株価指数データを Pub/Sub に送信しました。")

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
        for index_name, url in yahoo_finance_urls.items():
            get_stock_index_data(index_name, url)
        time.sleep(3600)  # 1時間(3600秒)ごとに実行

if __name__ == "__main__":
    main()