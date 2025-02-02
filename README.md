Markdown

# juntan-pulumi-project-v2

## 概要

本プロジェクトは、為替レート、経済指標、ニュースなどの金融データを収集・分析し、機械学習モデルを用いて将来の値動きを予測するためのシステムです。
リアルタイムデータと過去データを用いて、高精度な分析と予測を行います。
開発は、Google Cloud Platform (GCP) 上で行い、Dataflow, BigQuery, Pub/Sub, Cloud Functions, Cloud Run などのサービスを活用しています。

## 目的

*   リアルタイム為替レートデータを収集し、BigQueryに保存する。
*   各種経済指標データを収集し、BigQueryに保存する。
*   ニュースデータからセンチメント分析を行い、BigQueryに保存する。
*   収集したデータを用いて機械学習モデルを構築・学習し、将来の為替レートを予測する。
*   Dataflowパイプラインを用いて、データ収集・処理を自動化する。
*   開発・運用コストを最小限に抑える。
*   人的ミスを削減し、安定したシステム運用を実現する。
*   高速な処理と低遅延を実現し、快適な操作性を実現する。

## 使用技術

*   **プログラミング言語:** Python
*   **データ処理:** Dataflow, Apache Beam
*   **データウェアハウス:** BigQuery
*   **メッセージング:** Pub/Sub
*   **スケジューラ:** Cloud Scheduler (将来的には取得間隔を短くするため、Dataflow内でスケジューリング)
*   **関数:** Cloud Functions (第2世代), Cloud Run
*   **機械学習:** Vertex AI, BigQuery ML (予定)
*   **インフラ管理:** Pulumi
*   **CI/CD:** GitHub Actions, Docker
*   **その他:** Cloud Build, Cloud Buildpacks, Cloud Monitoring, Cloud Logging, Cloud Debugger, Cloud Profiler, Error Reporting, Cloud Security Command Center, Google Cloud Armor

## プロジェクト構成

juntan-pulumi-project-v2/
├── dataflow/                # Dataflowパイプライン関連のファイルを格納
│   ├── fx_pipeline/         # 為替レートデータ処理のパイプライン
│   │   ├── main.py          # Dataflowパイプラインのメインプログラム (USD/JPYを含む複数通貨ペア対応)
│   │   ├── setup.py         # パッケージのセットアップファイル
│   │   ├── requirements.txt # 依存パッケージを記述
│   │   └── utils/           # 共通関数などを配置するディレクトリ(必要に応じて作成)
│   │       └── init.py
│   ├── market_indices_pipeline/ # 金・原油価格、株価指数、VIX指数をまとめたパイプライン
│   │   ├── main.py
│   │   ├── setup.py
│   │   ├── requirements.txt
│   │   └── utils/
│   │       └── init.py
│   ├── news_pipeline/       # ニュースデータ処理のパイプライン
│   │   ├── main.py
│   │   ├── setup.py
│   │   ├── requirements.txt
│   │   └── utils/
│   │       └── init.py
│   └── technical_indicators_pipeline/ # テクニカル指標のパイプライン
│       ├── main.py
│       ├── setup.py
│       ├── requirements.txt
│       └── utils/
│           └── init.py
├── .github/workflows/       # GitHub Actionsの設定ファイルを格納
│   └── dataflow_deploy.yaml # Dataflowパイプラインのデプロイ用ワークフロー(例)
├── Dockerfile               # Dockerイメージのビルド設定
├── .gitignore               # Gitの管理対象外にするファイルを記述
└── README.md                # プロジェクトの説明などを記述


## データの流れ
[現状]
```mermaid
graph LR
    A[Cloud Run/Functions] -- 為替/経済指標/ニュースデータ取得 --> B(Pub/Sub);
    B -- データ受信 --> C{Dataflow};
    C -- 前処理 --> D[BigQuery];
    D -- ライフサイクルポリシー --> E(Cloud Storage);
[将来の構成案]

コード スニペット

graph LR
    A[Dataflow] -- データ取得 --> B(Pub/Sub);
    B -- データ受信 --> A;
    A -- 前処理 --> C[BigQuery];
    C -- ライフサイクルポリシー --> D(Cloud Storage);
セットアップ手順
Google Cloudプロジェクトを作成する。

必要なAPI（Dataflow, Pub/Sub, BigQuery, Compute Engine, Cloud Storageなど）を有効にする。

サービスアカウントを作成し、必要な権限を付与する。

Workload Identity連携を設定する。

GitHubリポジトリの「Settings」>「Secrets and variables」>「Actions」で必要なシークレット（APIキー、プロジェクトID、GCSバケット名など）を設定する。

必要なPythonパッケージをインストールする。

Bash

pip install -r requirements.txt
実行方法
Dataflowパイプラインを実行するには、以下のコマンドを実行します。

Bash

python dataflow/fx_pipeline/main.py \
  --project_id YOUR_PROJECT_ID \
  --region YOUR_REGION \
  --temp_location gs://YOUR_GCS_BUCKET/tmp \
  --runner DataflowRunner \
  --save_main_session \
  --setup_file ./dataflow/fx_pipeline/setup.py \
  --streaming
デプロイ方法
GitHub Actionsを使用して、Dataflowパイプラインを自動的にデプロイするように設定されています。mainブランチにコードをプッシュすると、自動的にパイプラインがデプロイされます。

コントリビューション
貢献方法については、CONTRIBUTING.mdを参照してください。

ライセンス
このプロジェクトは、MITライセンスの下で公開されています。LICENSEファイルを参照してください。

連絡先
質問や不明点がある場合は、あなたの名前までご連絡ください。

参考情報
Dataflow
BigQuery
Pub/Sub
Financial Modeling Prep API
Alpha Vantage API
FRED API
GNews API
News API
e-Stat API
世界銀行