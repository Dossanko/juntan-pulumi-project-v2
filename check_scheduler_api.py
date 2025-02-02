from googleapiclient.discovery import build

# プロジェクト ID を設定します
project_id = "juntan-project-448407"

# サービスを作成します
service = build('serviceusage', 'v1')

# Cloud Scheduler API の状態を取得します
request = service.services().get(name=f"projects/{project_id}/services/cloudscheduler.googleapis.com")
response = request.execute()

# Cloud Scheduler API が有効になっているか確認します
if response['state'] == 'ENABLED':
    print("Cloud Scheduler API は有効になっています。")
else:
    print("Cloud Scheduler API は無効になっています。")