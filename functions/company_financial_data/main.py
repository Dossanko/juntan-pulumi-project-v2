import os
import requests
from google.cloud import pubsub_v1
from google.cloud import scheduler_v1

# API キーを環境変数から取得します
api_key = os.environ.get('FINANCIAL_MODELING_PREP_API_KEY')

# Pub/Sub トピック ID を取得します
topic_id = os.environ.get('COMPANY_FINANCIAL_DATA_TOPIC_ID')

def get_company_financial_data(symbol):
    """
    Financial Modeling Prep API から企業財務データを取得し、Pub/Sub に送信する関数
    """
    # Financial Modeling Prep API のエンドポイント URL を設定します
    # ここでは、Income Statement のデータを取得する例を示します
    url = f"https://financialmodelingprep.com/api/v3/income-statement/{symbol}?apikey={api_key}"

    try:
        # API リクエストを送信します
        response = requests.get(url)
        response.raise_for_status()  # エラーレスポンスの場合、例外を発生させます

        # レスポンスデータを JSON 形式で取得します
        data = response.json()

        # Pub/Sub メッセージを送信します
        publish_message(topic_id, data)

        print(f"{symbol} の企業財務データを Pub/Sub に送信しました。")

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

def create_scheduler_job(job_id, schedule, topic_id, symbol):
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
        "body": f"{topic_id},{symbol}".encode(),  # Pub/Sub トピック ID とシンボルを body に設定
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
    # 必要に応じてデータを取得
    # ここでは、例として、"AAPL" と "MSFT" の企業財務データを取得します
    symbols = ["AAPL", "MSFT"]
    for symbol in symbols:
        get_company_financial_data(symbol)

        # Cloud Scheduler にジョブを作成
        job_id = f"get_company_financial_data_job_{symbol}"
        schedule = "0 0 * * *"  # 毎日0時0分に実行
        create_scheduler_job(job_id, schedule, topic_id, symbol)

    return 'OK'