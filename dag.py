import dagshub
dagshub.init(repo_owner='rafyardhani', repo_name='mlsystem-studi-kasus-cs', mlflow=True)
import mlflow
with mlflow.start_run():
  # Your training code here...
  mlflow.log_metric('accuracy', 42)
  mlflow.log_param('Param name', 'Value')