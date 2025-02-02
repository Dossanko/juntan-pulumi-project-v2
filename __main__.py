import pulumi
import pulumi_gcp as gcp

# 設定の読み込み
config = pulumi.Config()
project_id = config.require("project_id")
region = config.require("region")
service_account_email = config.require("service_account_email")
github_repository = config.require("github_repository")

# Workload Identity プールの作成
workload_identity_pool = gcp.iam.WorkloadIdentityPool("github-pool",
    project=project_id,
    workload_identity_pool_id="juntan-github-v2",
    display_name="juntan-github-v2",
    description="GitHub Actions Workload Identity Pool",
    disabled=False
)

# GitHub用のWorkload Identity プロバイダの作成
workload_identity_pool_provider = gcp.iam.WorkloadIdentityPoolProvider("github-provider",
    project=project_id,
    workload_identity_pool_id=workload_identity_pool.workload_identity_pool_id,
    workload_identity_pool_provider_id="github-actions-provider",
    display_name="GitHub Actions Provider",
    description="OIDC provider for GitHub Actions",
    attribute_mapping={
        "google.subject": "assertion.repository",
        "attribute.actor": "assertion.actor",
        "attribute.repository": "assertion.repository",
    },
    oidc=gcp.iam.WorkloadIdentityPoolProviderOidcArgs(
        issuer_uri="https://token.actions.githubusercontent.com",
    ),
    # 属性条件をここに追加
    attribute_condition=f"assertion.repository == '{github_repository}'",
)

# サービスアカウントに権限を付与
dataflow_admin_iam = gcp.projects.IAMMember("dataflow-admin-iam",
    project=project_id,
    role="roles/dataflow.admin",
    member=f"serviceAccount:{service_account_email}"
)

pubsub_editor_iam = gcp.projects.IAMMember("pubsub-editor-iam",
    project=project_id,
    role="roles/pubsub.editor",
    member=f"serviceAccount:{service_account_email}"
)

bigquery_data_editor_iam = gcp.projects.IAMMember("bigquery-data-editor-iam",
    project=project_id,
    role="roles/bigquery.dataEditor",
    member=f"serviceAccount:{service_account_email}"
)

storage_admin_iam = gcp.projects.IAMMember("storage-admin-iam",
    project=project_id,
    role="roles/storage.admin",
    member=f"serviceAccount:{service_account_email}"
)

# GitHub Actionsにサービスアカウントへの権限を付与
github_actions_iam = gcp.serviceaccount.IAMMember("github-actions-iam",
    service_account_id=f"projects/{project_id}/serviceAccounts/{service_account_email}",
    role="roles/iam.workloadIdentityUser",
    member=pulumi.Output.all(workload_identity_pool.name, github_repository).apply(
        lambda args: f"principalSet://iam.googleapis.com/{args[0]}/attribute.repository/{args[1]}"
    )
)