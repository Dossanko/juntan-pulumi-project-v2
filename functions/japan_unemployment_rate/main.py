import os
import time
import requests
from google.cloud import pubsub_v1
from google.cloud import scheduler_v1

# API キーを環境変数から取得します
api_key = os.environ.get('FRED_API_KEY')

# Pub/Sub トピック ID を取得します
topic_id = os.environ.get('JAPAN_UNEMPLOYMENT_RATE_TOPIC_ID')

def get_japan_unemployment_rate_data():
    """
    FRED API から日本の失業率データを取得し、Pub/Sub に送信する関数
    """
    # FRED API のエンドポイント URL を設定します
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=LRUNTTTTJPM156S&api_key={api_key}&file_type=json"

    try:
        # API リクエストを送信します
        response = requests.get(url)
        response.raise_for_status()  # エラーレスポンスの場合、例外を発生させます

        # レスポンスデータを JSON 形式で取得します
        data = response.json()

        # Pub/Sub メッセージを送信します
        publish_message(topic_id, data)

        print("日本失業率データを Pub/Sub に送信しました。")

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

def create_scheduler_job(job_id, schedule, topic_id):
    """
    Cloud Scheduler にジョブを作成する関数
    """
    # Cloud Scheduler クライアントを初期化します
    client = scheduler_v1.CloudSchedulerClient()

    # ジョブのロケーション、プロジェクト ID、ジョブ ID を設定します
    parent = f"projects/{os.environ.get('GCP_PROJECT')}/locations/{os.environ.get('GCP_REGION')}"
    job_name = f"{parent}/jobs/{job_id}"

    # HTTP リクエストを作成します
    http_target = {
        "uri": os.environ.get('FUNCTION_URL'),  # Cloud Functions の URL
        "http_method": 1,  # POST メソッド
        "headers": {
            "Content-Type": "application/octet-stream",
            "User-Agent": "Google-Cloud-Scheduler",
        },
        "body": topic_id.encode(),  # Pub/Sub トピック ID を body に設定
    }

    # ジョブを作成します
    job = {
        "name": job_name,
        "schedule": schedule,  # スケジュール (例: "0 0 * * *")
        "http_target": http_target,
        "time_zone": "Asia/Tokyo",  # タイムゾーン
    }

    try:
        # ジョブを作成します
        response = client.create_job(request={"parent": parent, "job": job})
        print(f"ジョブを作成しました: {response.name}")
    except Exception as e:
        print(f"ジョブの作成に失敗しました: {e}")

def main(request):
    # 最初の実行時にデータを取得
    get_japan_unemployment_rate_data()

    # Cloud Scheduler にジョブを作成
    job_id = "get_japan_unemployment_rate_job"
    schedule = "0 0 1 * *"  # 毎月1日の0時0分に実行
    create_scheduler_job(job_id, schedule, topic_id)

    return 'OK'