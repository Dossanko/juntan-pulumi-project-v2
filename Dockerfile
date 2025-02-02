# ベースイメージを指定
FROM python:3.12-slim

# 環境変数を設定
ENV APP_HOME=/app
WORKDIR $APP_HOME

# 必要なパッケージをインストール
COPY dataflow/fx_pipeline/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# プロジェクトのファイルをコピー
COPY . .

# Dataflowパイプラインのエントリポイントを指定
CMD ["python", "dataflow/fx_pipeline/main.py"]