import os
import time
from google.cloud import pubsub_v1
from google.cloud import scheduler_v1
from newspaper import Article

# ニュースAPIのAPIキーを取得します
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')

# Pub/Sub トピック ID を取得します
topic_id = os.environ.get('NEWS_SENTIMENT_TOPIC_ID')

def get_news_sentiment(url):
    """
    指定されたURLのニュース記事のセンチメントを分析する関数
    """
    try:
        # 記事をダウンロードしてパースします
        article = Article(url)
        article.download()
        article.parse()

        # 記事のセンチメントを分析します
        # ここでは、センチメント分析のロジックを実装する必要があります
        # 例として、記事のタイトルと本文からポジティブ/ネガティブな単語をカウントする
        positive_words = ["good", "positive", "increase", "growth"]
        negative_words = ["bad", "negative", "decrease", "decline"]
        positive_count = sum([article.title.lower().count(word) + article.text.lower().count(word) for word in positive_words])
        negative_count = sum([article.title.lower().count(word) + article.text.lower().count(word) for word in negative_words])
        sentiment = "positive" if positive_count > negative_count else "negative"

        # 結果をPub/Subに送信します
        publish_message(topic_id, {"url": url, "sentiment": sentiment})

        print(f"ニュース記事のセンチメント: {sentiment}")

    except Exception as e:
        print(f"エラー: {e}")

def get_news_data():
    """
    News APIからニュースデータを取得する関数
    """
    try:
        # News APIのエンドポイントURLを設定します
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"

        # APIリクエストを送信します
        response = requests.get(url)
        response.raise_for_status()  # エラーレスポンスの場合、例外を発生させます

        # レスポンスデータをJSON形式で取得します
        data = response.json()

        # 各記事のURLを取得し、センチメントを分析します
        for article in data["articles"]:
            get_news_sentiment(article["url"])

    except requests.exceptions.RequestException as e:
        print(f"APIリクエストエラー: {e}")
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
    get_news_data()

    # Cloud Scheduler にジョブを作成
    job_id = "get_news_sentiment_job"
    schedule = "0 * * * *"  # 毎時0分に実行
    create_scheduler_job(job_id, schedule, topic_id)

    return 'OK'