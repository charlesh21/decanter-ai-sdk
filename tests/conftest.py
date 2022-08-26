import pytest
# from test_mock_iid import test_iid
# from test_mock_ts import test_ts

import sys

sys.path.append("..")
from decanter_ai_sdk.client import Client
import os
from decanter_ai_sdk.enums.evaluators import ClassificationMetric, RegressionMetric
from decanter_ai_sdk.enums.data_types import DataType
from decanter_ai_sdk.enums.time_units import TimeUnit
import pandas as pd
from typing import List

class Test_demo():
    def test_iid():
        print("---From test iid---")

        client = Client(
            auth_key="auth_API_key",
            project_id="project_id",
            host="host_url",
            dry_run_type="iid",
        )

        current_path = os.path.dirname(os.path.abspath(__file__))

        train_file_path = os.path.join(current_path, "train.csv")
        train_file = open(train_file_path, "rb")
        train_id = client.upload(train_file, "train_file")

        test_file_path = os.path.join(current_path, "test.csv")
        test_file = open(test_file_path, "rb")
        test_id = client.upload(test_file, "test_file")

        assert isinstance(client.get_table_list(), List)
        assert client.get_table_list().__len__() == 2
        assert client.get_table_list()[0]["name"] == "train_file"
        assert client.get_table_list()[1]["name"] == "test_file"

        exp_name = "exp_name"
        experiment = client.train_iid(
            experiment_name=exp_name,
            experiment_table_id=train_id,
            target="Survived",
            evaluator=ClassificationMetric.AUC,
            custom_feature_types={
                "Pclass": DataType.categorical,
                "Parch": DataType.categorical,
            },
        )

        best_model = experiment.get_best_model()
        assert (
            experiment.get_best_model_by_metric(
                ClassificationMetric.MISCLASSIFICATION
            ).model_id
            == "630439eced266c3d7b2f83f6"
        )
        assert (
            experiment.get_best_model_by_metric(ClassificationMetric.AUC).model_id
            == "630439f8ed266c3d7b2f83fa"
        )
        assert (
            experiment.get_best_model_by_metric(
                ClassificationMetric.LIFT_TOP_GROUP
            ).model_id
            == "630439f6ed266c3d7b2f83f9"
        )
        assert (
            experiment.get_best_model_by_metric(ClassificationMetric.LOGLOSS).model_id
            == "630439fbed266c3d7b2f83fb"
        )
        assert (
            experiment.get_best_model_by_metric(
                ClassificationMetric.MEAN_PER_CLASS_ERROR
            ).model_id
            == "630439fbed266c3d7b2f83fb"
        )

        assert isinstance(experiment.get_model_list(), List)
        assert experiment.get_model_list().__len__() == 7
        for model in experiment.get_model_list():
            assert model.experiment_id == "630439e3818547e247f5aa3d"
        assert experiment.experiment_info()["name"] == exp_name

        predict = client.predict_iid(
            keep_columns=[], non_negative=False, test_table_id=test_id, model=best_model
        )

        assert isinstance(predict.get_predict_df(), pd.DataFrame)
        assert predict.attributes['model_id'] == best_model.model_id
        assert predict.attributes['table_id'] == test_id
        
    def test_ts():
        print("---From test ts---")

        client = Client(
            auth_key="auth_API_key",
            project_id="project_id",
            host="host_url",
            dry_run_type="ts",
        )

        current_path = os.path.dirname(os.path.abspath(__file__))

        train_file_path = os.path.join(current_path, "ts_train.csv")
        train_file = open(train_file_path, "rb")
        train_id = client.upload(train_file, "train_file")

        test_file_path = os.path.join(current_path, "ts_test.csv")
        test_file = open(test_file_path, "rb")
        test_id = client.upload(test_file, "test_file")

        assert isinstance(client.get_table_list(), List)
        assert client.get_table_list().__len__() == 2
        assert client.get_table_list()[0]["name"] == "train_file"
        assert client.get_table_list()[1]["name"] == "test_file"

        exp_name = "exp_name"
        experiment = client.train_ts(
            experiment_name=exp_name,
            experiment_table_id=train_id,
            target="Passengers",
            datetime="Month",
            time_groups=[],
            timeunit=TimeUnit.month,
            groupby_method="sum",
            max_model=5,
            evaluator=RegressionMetric.MAPE,
            custom_feature_types={"Pclass": DataType.numerical},
        )

        best_model = experiment.get_best_model()

        for metric in RegressionMetric:
            assert (
                experiment.get_best_model_by_metric(metric).model_id
                == "63044b72ed266c3d7b2f895f"
            )

        assert isinstance(experiment.get_model_list(), List)
        assert experiment.get_model_list().__len__() == 4
        for model in experiment.get_model_list():
            assert model.experiment_id == "63044b583a6eef99be6e8e9b"
        assert experiment.experiment_info()["name"] == exp_name

        predict = client.predict_ts(
            keep_columns=[], non_negative=False, test_table_id=test_id, model=best_model
        )

        assert isinstance(predict.get_predict_df(), pd.DataFrame)
        assert predict.attributes['model_id'] == best_model.model_id
        assert predict.attributes['table_id'] == test_id
        
if __name__ == "__name__":
    pytest.main()