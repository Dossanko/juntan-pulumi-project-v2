# -*- coding: utf-8 -*-
import apache_beam as beam
import json
from apache_beam.transforms.window import FixedWindows

# 為替レートデータの前処理を行う関数
def preprocess_fx_data(data):
    # 通貨ペアをキーとして使用する例
    key = data.get("currency_pair", "default_key")

    # 必要なデータの抽出
    processed_data = {
        "timestamp": data["timestamp"],
        "open": data["open"],
        "high": data["high"],
        "low": data["low"],
        "close": data["close"],
    }
    return (key, processed_data)

# 経済指標データの前処理を行う関数
def preprocess_economic_indicator_data(data):
    # 指標名をキーとして使用する例
    key = data.get("indicator_name", "default_key")

    processed_data = {
        "date": data["date"],
        "value": data["value"],
    }
    return (key, processed_data)

# ニュースデータの前処理を行う関数
def preprocess_news_data(data):
    # ニュースソースをキーとして使用する例
    key = data.get("source", "default_key")

    processed_data = {
        "published_at": data["publishedAt"],
        "title": data["title"],
        "description": data["description"],
        "sentiment": data["sentiment"],
    }
    return (key, processed_data)

# ウィンドウ内の最初の要素を選択する関数
def pick_first_element(elements):
    return elements[0] if elements else None

with beam.Pipeline() as pipeline:
    # 為替レートデータ
    fx_data = (
        pipeline
        | "ReadFXDataFromPubSub" >> beam.io.ReadFromPubSub(topic="projects/juntan-project-448407/topics/fx-rates-topic")
        | "DecodeFXData" >> beam.Map(lambda x: x.decode("utf-8"))
        | "ParseJsonFXData" >> beam.Map(json.loads)
        | "PreprocessFXData" >> beam.Map(preprocess_fx_data)
        | "WindowFXData" >> beam.WindowInto(FixedWindows(60))
        | "GroupByKeyFXData" >> beam.GroupByKey()
        | "GetFirstElementFXData" >> beam.Map(lambda x: (x[0], pick_first_element(x[1])))
        | "PrepareFXDataForBigQuery" >> beam.Map(lambda x: {
            "timestamp": x[1]["timestamp"],
            "open": x[1]["open"],
            "high": x[1]["high"],
            "low": x[1]["low"],
            "close": x[1]["close"],
        })
        | "WriteToBigQueryFXData" >> beam.io.WriteToBigQuery(
            table="juntan-project-448407:my_dataset.fx_rates",
            schema="timestamp:TIMESTAMP,open:FLOAT64,high:FLOAT64,low:FLOAT64,close:FLOAT64",
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
        )
    )

    # 経済指標データ
    economic_indicator_data = (
        pipeline
        | "ReadEconomicIndicatorDataFromPubSub" >> beam.io.ReadFromPubSub(topic="projects/juntan-project-448407/topics/economic-indicators-topic")
        | "DecodeEconomicIndicatorData" >> beam.Map(lambda x: x.decode("utf-8"))
        | "ParseJsonEconomicIndicatorData" >> beam.Map(json.loads)
        | "PreprocessEconomicIndicatorData" >> beam.Map(preprocess_economic_indicator_data)
        | "WindowEconomicIndicatorData" >> beam.WindowInto(FixedWindows(60))
        | "GroupByKeyEconomicIndicatorData" >> beam.GroupByKey()
        | "GetFirstElementEconomicIndicatorData" >> beam.Map(lambda x: (x[0], pick_first_element(x[1])))
        | "PrepareEconomicIndicatorDataForBigQuery" >> beam.Map(lambda x: {
            "date": x[1]["date"],
            "value": x[1]["value"],
        })
        | "WriteToBigQueryEconomicIndicatorData" >> beam.io.WriteToBigQuery(
            table="juntan-project-448407:my_dataset.economic_indicators",
            schema="date:DATE,value:FLOAT64",
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
        )
    )

    # ニュースデータ
    news_data = (
        pipeline
        | "ReadNewsDataFromPubSub" >> beam.io.ReadFromPubSub(topic="projects/juntan-project-448407/topics/news-topic")
        | "DecodeNewsData" >> beam.Map(lambda x: x.decode("utf-8"))
        | "ParseJsonNewsData" >> beam.Map(json.loads)
        | "PreprocessNewsData" >> beam.Map(preprocess_news_data)
        | "WindowNewsData" >> beam.WindowInto(FixedWindows(60))
        | "GroupByKeyNewsData" >> beam.GroupByKey()
        | "GetFirstElementNewsData" >> beam.Map(lambda x: (x[0], pick_first_element(x[1])))
        | "PrepareNewsDataForBigQuery" >> beam.Map(lambda x: {
            "published_at": x[1]["published_at"],
            "title": x[1]["title"],
            "description": x[1]["description"],
            "sentiment": x[1]["sentiment"],
        })
        | "WriteToBigQueryNewsData" >> beam.io.WriteToBigQuery(
            table="juntan-project-448407:my_dataset.news",
            schema="published_at:TIMESTAMP,title:STRING,description:STRING,sentiment:STRING",
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
        )
    )