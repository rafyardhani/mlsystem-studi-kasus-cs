import mlflow
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import random
import numpy as np

mlflow.set_tracking_uri(uri="http://127.0.0.1:5000/")

# Create a new MLflow Experiment
mlflow.set_experiment("Latihan Credit Scoring")

data = pd.read_csv("train_pca.csv")

X_train, X_test, y_train, y_test = train_test_split(data.drop("Credit_Score", axis=1), data["Credit_Score"], random_state=42, test_size=0.2)
input_example = X_train[0:5]

# Define Elastic Search parameters
n_estimators_range = np.linspace(10, 1000, 5, dtype=int)  # 5 evenly spaced values
max_depth_range = np.linspace(1, 50, 5, dtype=int)  # 5 evenly spaced values

best_accuracy = 0
best_params = {}

with mlflow.start_run():
    # Log parameters
    n_estimators = random.randint(0,1000)
    max_depth = random.randint(1,50)
    mlflow.autolog()
    # Train model
    model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth)
    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="model",
        input_example=input_example
    )
    model.fit(X_train, y_train)
    # Log metrics
    accuracy = model.score(X_test, y_test)
    mlflow.log_metric("accuracy", accuracy)
# Mendifinisikan model menggunakan hyperparameter tuning.
# # Define Elastic Search parameters
# n_estimators_range = np.linspace(10, 1000, 5, dtype=int)  # 5 evenly spaced values
# max_depth_range = np.linspace(1, 50, 5, dtype=int)  # 5 evenly spaced values

# best_accuracy = 0
# best_params = {}

# for n_estimators in n_estimators_range:
#     for max_depth in max_depth_range:
#         with mlflow.start_run(run_name=f"elastic_search_{n_estimators}_{max_depth}"):
#             mlflow.autolog()

#             # Train model
#             model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
#             model.fit(X_train, y_train)

#             # Evaluate model
#             accuracy = model.score(X_test, y_test)
#             mlflow.log_metric("accuracy", accuracy)

#             # Save the best model
#             if accuracy > best_accuracy:
#                 best_accuracy = accuracy
#                 best_params = {"n_estimators": n_estimators, "max_depth": max_depth}
#                 mlflow.sklearn.log_model(
#                     sk_model=model,
#                     artifact_path="model",
#                     input_example=input_example
#                     )