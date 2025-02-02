import setuptools

setuptools.setup(
    name="fx-pipeline",
    version="0.1.0",
    description="Dataflow pipeline for processing FX rates",
    install_requires=[
        "apache-beam[gcp]>=2.62.0",  # 最小バージョン指定に変更
        "requests>=2.24.0",
        "google-cloud-pubsub>=2.13.0",
        "google-cloud-storage>=2.19.0",
    ],
    packages=setuptools.find_packages(), # dataflow/fx_pipeline内のパッケージを自動検出
    # packages=['dataflow', 'dataflow.fx_pipeline', 'dataflow.fx_pipeline.utils'], # パッケージを明示的に指定する場合
)