import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from apache_beam.transforms.window import FixedWindows
from apache_beam.transforms.trigger import AfterWatermark, AfterProcessingTime, AccumulationMode
import json
import requests
import time
import logging
import argparse
import os

# 環境変数から設定を読み込む
API_KEY = os.environ.get("FINANCIAL_MODELING_PREP_API_KEY")
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
PUBSUB_TOPIC_USDJPY = os.environ.get("FX_RATES_USDJPY_TOPIC_ID")
PUBSUB_TOPIC_EURUSD = os.environ.get("FX_RATES_EURUSD_TOPIC_ID")
PUBSUB_TOPIC_GBPJPY = os.environ.get("FX_RATES_GBPJPY_TOPIC_ID")
PUBSUB_TOPIC_GBPUSD = os.environ.get("FX_RATES_GBPUSD_TOPIC_ID")
PUBSUB_TOPIC_EURJPY = os.environ.get("FX_RATES_EURJPY_TOPIC_ID")

BIGQUERY_DATASET = "fx_dataset"  # BigQueryのデータセット名
BIGQUERY_TABLE = "fx_rates"  # BigQueryのテーブル名

# データ取得間隔(秒)
POLLING_INTERVAL = 5  # 例：5秒ごとにデータ取得

# ウィンドウサイズ(秒)
WINDOW_SIZE = 60  # 例：60秒間のウィンドウ

# エラー時のリトライ回数
RETRY_COUNT = 3

class GetFXData(beam.DoFn):
    """
    Financial Modeling Prep APIから為替データを取得するDoFn
    """

    def __init__(self, api_key):
        self.api_key = api_key

    def process(self, element):
        currency_pair = element
        url = f"https://financialmodelingprep.com/api/v3/forex/{currency_pair}?apikey={self.api_key}"

        for attempt in range(RETRY_COUNT + 1):
          try:
              response = requests.get(url, timeout=10)
              response.raise_for_status()
              data = response.json()

              processed_data = {
                  "currency_pair": currency_pair,
                  "timestamp": data[0]["date"],  # 実際のデータ構造に合わせて変更
                  "open": float(data[0]["open"]),
                  "high": float(data[0]["high"]),
                  "low": float(data[0]["low"]),
                  "close": float(data[0]["close"]),
              }
              logging.info(f"Successfully fetched data for {currency_pair}: {processed_data}")
              return [(currency_pair, processed_data)]
          except requests.exceptions.RequestException as e:
              logging.warning(f"Attempt {attempt + 1} failed for {currency_pair}: {e}")
              if attempt < RETRY_COUNT:
                  time.sleep(2 ** attempt)  # 指数バックオフでリトライ間隔を増やす
              else:
                logging.error(f"Failed to fetch data for {currency_pair} after multiple retries: {e}")
                raise

class PublishToPubSub(beam.DoFn):
    """
    Pub/Subにメッセージを発行するDoFn
    """

    def __init__(self, topic):
        self.topic = topic

    def setup(self):
        from google.cloud import pubsub_v1
        self.publisher = pubsub_v1.PublisherClient()

    def process(self, element):
        currency_pair, data = element
        topic_path = self.publisher.topic_path(PROJECT_ID, self.topic)

        message_data = json.dumps(data).encode("utf-8")
        future = self.publisher.publish(topic_path, message_data)

        logging.info(f"Published message to {self.topic}: {future.result()}")

        yield data

class CustomMappingFn(beam.DoFn):
    def process(self, element):
        # 必要に応じて、ここでデータのマッピング処理を実装
        # 例：タイムスタンプのフォーマット変更など
        return [element]
    
# ウィンドウ内の最初の要素を選択する関数
def pick_first_element(elements):
    return elements[0] if elements else None

def run_pipeline(pipeline_options):
    with beam.Pipeline(options=pipeline_options) as pipeline:
        currency_pairs = ["USDJPY", "EURUSD", "GBPJPY", "GBPUSD", "EURJPY"]
        currency_topics = {
            "USDJPY": PUBSUB_TOPIC_USDJPY,
            "EURUSD": PUBSUB_TOPIC_EURUSD,
            "GBPJPY": PUBSUB_TOPIC_GBPJPY,
            "GBPUSD": PUBSUB_TOPIC_GBPUSD,
            "EURJPY": PUBSUB_TOPIC_EURJPY,
        }
        currency_pairs_pcoll = pipeline | "Create Currency Pairs" >> beam.Create(currency_pairs)

        for currency_pair in currency_pairs:
            fx_data = (
                currency_pairs_pcoll
                | f"Get FX Data for {currency_pair}" >> beam.ParDo(GetFXData(API_KEY))
                | f"Window FX Data for {currency_pair}" >> beam.WindowInto(FixedWindows(WINDOW_SIZE),
                                                                        trigger=AfterWatermark(
                                                                            early=AfterProcessingTime(WINDOW_SIZE)),
                                                                        accumulation_mode=AccumulationMode.DISCARDING)
                | f"Publish to PubSub {currency_pair}" >> beam.ParDo(PublishToPubSub(currency_topics[currency_pair]))
                | f"GroupByKey {currency_pair}" >> beam.GroupByKey()
                | f"GetFirstElement {currency_pair}" >> beam.Map(lambda x: (x[0], pick_first_element(x[1])))
                | f"ExtractValue {currency_pair}" >> beam.Map(lambda x: x[1])
                | f"Custom Mapping for {currency_pair}" >> beam.ParDo(CustomMappingFn())
                | f"Reshuffle {currency_pair}" >> beam.Reshuffle()
            )

            (fx_data
                | f"Write to BigQuery {currency_pair}" >> beam.io.WriteToBigQuery(
                    table=f"{currency_pair.lower()}_table",  # 通貨ペアごとのテーブル名
                    dataset=BIGQUERY_DATASET,
                    project=PROJECT_ID,
                    schema="currency_pair:STRING,timestamp:TIMESTAMP,open:FLOAT,high:FLOAT,low:FLOAT,close:FLOAT",
                    create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                    write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                )
            )

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_id", required=True, help="Google Cloud Project ID")
    parser.add_argument("--region", required=True, help="Dataflow Region")
    parser.add_argument("--temp_location", required=True, help="GCS Temp Location")
    parser.add_argument("--runner", default="DirectRunner", help="Pipeline Runner")
    known_args, pipeline_args = parser.parse_known_args()

    pipeline_options = PipelineOptions(
        pipeline_args,
        runner=known_args.runner,
        project=known_args.project_id,
        region=known_args.region,
        temp_location=known_args.temp_location,
        staging_location=f"{known_args.temp_location}/staging",
        setup_file="./setup.py",
        save_main_session=True,
        streaming=False,  # バッチモードで実行
    )

    run_pipeline(pipeline_options)