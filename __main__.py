import pulumi
import pulumi_gcp as gcp

# Google Cloud プロジェクトの ID を指定します
project_id = "juntan-project-448407"

# Cloud Storage バケットを作成します
bucket = gcp.storage.Bucket("juntan-fx-data-bucket",
    name="juntan-project-pulumi",  # バケット名を指定
    location="ASIA-NORTHEAST1",  # リージョンを指定
    storage_class="STANDARD",  # ストレージクラスを指定
    public_access_prevention="enforced",  # 公開アクセスを無効にする
    versioning={"enabled": True},  # バージョニングを有効にする
    project=project_id)

# Pub/Sub トピックを作成します
topic = gcp.pubsub.Topic("juntan-fx-data-topic",
    project=project_id)

# リソースの情報をエクスポートします
pulumi.export("bucket_name", bucket.name)
pulumi.export("topic_name", topic.name)