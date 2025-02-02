import os
import requests
from google.cloud import pubsub_v1

# API キーを環境変数から取得します
fred_api_key = os.environ.get('FRED_API_KEY')
alpha_vantage_api_key = os.environ.get('ALPHA_VANTAGE_API_KEY')

# Pub/Sub トピック ID を取得します
topic_id = os.environ.get('MAJOR_ECONOMIC_INDICATORS_TOPIC_ID')

def get_economic_indicator_data(indicator_id, api_key, api_provider="fred"):
    """
    FRED API または Alpha Vantage API から経済指標データを取得し、Pub/Sub に送信する関数
    """
    try:
        if api_provider == "fred":
            # FRED API のエンドポイント URL を設定します
            url = f"https://api.stlouisfed.org/fred/series/observations?series_id={indicator_id}&api_key={api_key}&file_type=json"
        elif api_provider == "alpha_vantage":
            # Alpha Vantage API のエンドポイント URL を設定します
            url = f"https://www.alphavantage.co/query?function=ECONOMIC_INDICATOR&symbol={indicator_id}&apikey={api_key}"
        else:
            raise ValueError("無効な API プロバイダーが指定されました。")

        # API リクエストを送信します
        response = requests.get(url)
        response.raise_for_status()  # エラーレスポンスの場合、例外を発生させます

        # レスポンスデータを JSON 形式で取得します
        data = response.json()

        # Pub/Sub メッセージを送信します
        publish_message(topic_id, data)

        print(f"{indicator_id} の経済指標データを Pub/Sub に送信しました。")

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

def main(request):
    # 経済指標 ID と API キーのリスト
    indicators = [
        ("GDP", fred_api_key, "fred"),  # 米国 GDP (FRED API)
        ("UNRATE", fred_api_key, "fred"),  # 米国失業率 (FRED API)
        ("FEDFUNDS", fred_api_key, "fred"),  # 米国金利 (FRED API)
        ("BOPGSTB", fred_api_key, "fred"),  # 米国貿易収支 (FRED API)
        ("CPIAUCSL", fred_api_key, "fred"),  # 米国 CPI (FRED API)
        ("PPIACO", fred_api_key, "fred"),  # 米国 PPI (FRED API)
        ("ISMPMI", fred_api_key, "fred"),  # 米国 PMI (FRED API)
        ("RSAFS", fred_api_key, "fred"),  # 米国小売売上高 (FRED API)
        ("INDPRO", fred_api_key, "fred"),  # 米国鉱工業生産指数 (FRED API)
        ("DGORDER", fred_api_key, "fred"),  # 米国耐久財受注 (FRED API)
        ("ISM", fred_api_key, "fred"),  # 米国 ISM 製造業景況指数 (FRED API)
        ("ISMNON", fred_api_key, "fred"),  # 米国 ISM 非製造業景況指数 (FRED API)
        ("HOUST", fred_api_key, "fred"),  # 米国住宅着工件数 (FRED API)
        ("UMCSENT", fred_api_key, "fred"),  # 米国消費者信頼感指数 (FRED API)
        ("JPNNGDP", alpha_vantage_api_key, "alpha_vantage"),  # 日本 GDP (Alpha Vantage API)
        ("JPNUNEMP", alpha_vantage_api_key, "alpha_vantage"),  # 日本失業率 (Alpha Vantage API)
        ("JPNRATE", alpha_vantage_api_key, "alpha_vantage"),  # 日本金利 (Alpha Vantage API)
        ("JPNTRADE", alpha_vantage_api_key, "alpha_vantage"),  # 日本貿易収支 (Alpha Vantage API)
        ("JPNCPI", alpha_vantage_api_key, "alpha_vantage"),  # 日本 CPI (Alpha Vantage API)
        ("JPNPPI", alpha_vantage_api_key, "alpha_vantage"),  # 日本 PPI (Alpha Vantage API)
        ("JPNPMI", alpha_vantage_api_key, "alpha_vantage"),  # 日本 PMI (Alpha Vantage API)
    ]

    # 各指標のデータを取得
    for indicator_id, api_key, api_provider in indicators:
        get_economic_indicator_data(indicator_id, api_key, api_provider)

    return 'OK'