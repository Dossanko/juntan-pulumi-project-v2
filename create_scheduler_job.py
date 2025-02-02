from google.cloud import scheduler_v1

# プロジェクト ID を設定します
project_id = "juntan-project-448407"

# ロケーションを設定します
location_id = "asia-northeast1"

# Cloud Scheduler クライアントを初期化します
client = scheduler_v1.CloudSchedulerClient()

# ジョブのリスト
jobs = [
    {
        "job_id": "get-major-economic-indicators-job",
        "schedule": "0 0 * * *",  # 毎日0時に実行
        "function_url": "https://asia-northeast1-juntan-project-448407.cloudfunctions.net/major_economic_indicators",
        "topic_id": "major-economic-indicators-topic",
    },
    {
        "job_id": "get-us-gdp-job",
        "schedule": "0 0 1 */3 *",  # 3ヶ月ごとに1日の0時に実行
        "function_url": "https://asia-northeast1-juntan-project-448407.cloudfunctions.net/us_gdp",
        "topic_id": "us-gdp-topic",
    },
    {
        "job_id": "get-us-unemployment-rate-job",
        "schedule": "0 0 1 * *",  # 毎月1日の0時に実行
        "function_url": "https://asia-northeast1-juntan-project-448407.cloudfunctions.net/us_unemployment_rate",
        "topic_id": "us-unemployment-rate-topic",
    },
    {
        "job_id": "get-us-interest-rate-job",
        "schedule": "0 0 * * 1",  # 毎週月曜日の0時に実行
        "function_url": "https://asia-northeast1-juntan-project-448407.cloudfunctions.net/us_interest_rate",
        "topic_id": "us-interest-rate-topic",
    },
    {
        "job_id": "get-us-trade-balance-job",
        "schedule": "0 0 1 * *",  # 毎月1日の0時に実行
        "function_url": "https://asia-northeast1-juntan-project-448407.cloudfunctions.net/us_trade_balance",
        "topic_id": "us-trade-balance-topic",
    },
    {
        "job_id": "get-us-current-account-balance-job",
        "schedule": "0 0 1 * *",  # 毎月1日の0時に実行
        "function_url": "https://asia-northeast1-juntan-project-448407.cloudfunctions.net/us_current_account_balance",
        "topic_id": "us-current-account-balance-topic",
    },
    {
        "job_id": "get-us-cpi-job",
        "schedule": "0 0 1 * *",  # 毎月1日の0時に実行
        "function_url": "https://asia-northeast1-juntan-project-448407.cloudfunctions.net/us_cpi",
        "topic_id": "us-cpi-topic",
    },
    {
        "job_id": "get-us-ppi-job",
        "schedule": "0 0 1 * *",  # 毎月1日の0時に実行
        "function_url": "https://asia-northeast1-juntan-project-448407.cloudfunctions.net/us_ppi",
        "topic_id": "us-ppi-topic",
    },
    {
        "job_id": "get-us-pmi-job",
        "schedule": "0 0 1 * *",  # 毎月1日の0時に実行
        "function_url": "https://asia-northeast1-juntan-project-448407.cloudfunctions.net/us_pmi",
        "topic_id": "us-pmi-topic",
    },
    {
        "job_id": "get-japan-gdp-job",
        "schedule": "0 0 1 1-12/3 *",  # 3ヶ月ごとに1日の0時に実行
        "function_url": "https://asia-northeast1-juntan-project-448407.cloudfunctions.net/japan_gdp",
        "topic_id": "japan-gdp-topic",
    },
    {
        "job_id": "get-news-sentiment-job",
        "schedule": "0 * * * *",  # 毎時0分に実行
        "function_url": "https://asia-northeast1-juntan-project-448407.cloudfunctions.net/news_sentiment",
        "topic_id": "news-sentiment-topic",
    },
    {
        "job_id": "get-moving-averages-job",
        "schedule": "0 * * * *",  # 毎時0分に実行
        "function_url": "https://asia-northeast1-juntan-project-448407.cloudfunctions.net/moving_averages",
        "topic_id": "moving-averages-topic",
    },
    {
        "job_id": "get-technical-indicators-job",
        "schedule": "0 */4 * * *",  # 4時間ごとに実行
        "function_url": "https://asia-northeast1-juntan-project-448407.cloudfunctions.net/technical_indicators",
        "topic_id": "technical-indicators-topic",
    },
    {
        "job_id": "get-company-financial-data-job",
        "schedule": "0 0 * * *",  # 毎日0時に実行
        "function_url": "https://asia-northeast1-juntan-project-448407.cloudfunctions.net/company_financial_data",
        "topic_id": "company-financial-data-topic",
    },
    {
        "job_id": "get-japan-cpi-job",
        "schedule": "0 0 1 * *",  # 毎月1日の0時に実行
        "function_url": "https://asia-northeast1-juntan-project-448407.cloudfunctions.net/japan_cpi",
        "topic_id": "japan-cpi-topic",
    },
    {
        "job_id": "get-japan-pmi-job",
        "schedule": "0 0 1 * *",  # 毎月1日の0時に実行
        "function_url": "https://asia-northeast1-juntan-project-448407.cloudfunctions.net/japan_pmi",
        "topic_id": "japan-pmi-topic",
    },
    {
        "job_id": "get-japan-ppi-job",
        "schedule": "0 0 1 * *",  # 毎月1日の0時に実行
        "function_url": "https://asia-northeast1-juntan-project-448407.cloudfunctions.net/japan_ppi",
        "topic_id": "japan-ppi-topic",
    },
    {
        "job_id": "get-japan-trade-balance-job",
        "schedule": "0 0 1 * *",  # 毎月1日の0時に実行
        "function_url": "https://asia-northeast1-juntan-project-448407.cloudfunctions.net/japan_trade_balance",
        "topic_id": "japan-trade-balance-topic",
    },
    {
        "job_id": "get-japan-unemployment-rate-job",
        "schedule": "0 0 1 * *",  # 毎月1日の0時に実行
        "function_url": "https://asia-northeast1-juntan-project-448407.cloudfunctions.net/japan_unemployment_rate",
        "topic_id": "japan-unemployment-rate-topic",
    },
    {
        "job_id": "get-japan-interest-rate-job",
        "schedule": "0 0 * * 1",  # 毎週月曜日の0時に実行
        "function_url": "https://asia-northeast1-juntan-project-448407.cloudfunctions.net/japan_interest_rate",
        "topic_id": "japan-interest-rate-topic",
    },
    {
        "job_id": "get-japan-current-account-balance-job",
        "schedule": "0 0 1 * *",  # 毎月1日の0時に実行
        "function_url": "https://asia-northeast1-juntan-project-448407.cloudfunctions.net/japan_current_account_balance",
        "topic_id": "japan-current-account-balance-topic",
    },
]

def create_scheduler_job(job_id, schedule, function_url, topic_id):
    """
    Cloud Scheduler にジョブを作成する関数
    """
    # ジョブのロケーション、プロジェクト ID、ジョブ ID を設定します
    parent = f"projects/{project_id}/locations/{location_id}"
    job_name = f"{parent}/jobs/{job_id}"

    # HTTP リクエストを作成します
    http_target = {
        "uri": function_url,  # Cloud Functions の URL
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

def main():
    for job in jobs:
        create_scheduler_job(job['job_id'], job['schedule'], job['function_url'], job['topic_id'])

if __name__ == "__main__":
    main()