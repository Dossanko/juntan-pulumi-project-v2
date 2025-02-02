#!/bin/bash

# Cloud Build を実行し、コンテナイメージをビルド・push
gcloud builds submit --config cloudbuild.yaml .

# Cloud Run サービスをデプロイ
gcloud run deploy juntan-fx-data-service-v2 --image gcr.io/$PROJECT_ID/get-fx-rates_v2 --region asia-northeast1 --platform managed