from ast import Dict
import os
import pandas as pd
from decanter_ai_sdk.enums.algorithms import IIDAlgorithms
from decanter_ai_sdk.enums.evaluators import ClassificationMetric
from decanter_ai_sdk.enums.data_types import DataType
from typing import Any, List
from setup import *


def test_train_and_predict_titanic(client):
    print("---From test iid with default titanic---")
    current_path = os.path.dirname(os.path.abspath(__file__))

    train_file_path = "data/train.csv"
    train_df = pd.read_csv(open(train_file_path, "rb"))
    train_id = client.upload(train_df, "train_file")
    assert train_id is not None

    test_file_path = "data/test.csv"
    test_file = open(test_file_path, "rb")
    test_id = client.upload(test_file, "test_file")
    assert test_id is not None
    assert isinstance(client.get_table_list(), List)

    client.update_table(table_id=train_id,
                        updated_column='Pclass',
                        updated_type= DataType.categorical.value)
    exp_name = "exp_test_iid"
    experiment = client.train_iid(
        experiment_name=exp_name,
        experiment_table_id=train_id,
        target="Survived",
        evaluator=ClassificationMetric.AUC,
        custom_column_types={
            "Pclass": DataType.categorical,
            "Parch": DataType.categorical,
        },
        algos=["GLM", "GBM", IIDAlgorithms.DRF, IIDAlgorithms.XGBoost],
    )

    assert experiment.status == "done"
    assert isinstance(experiment.get_model_list(), List)

    best_model = experiment.get_best_model()

    predict = client.predict_iid(
        keep_columns=[],
        non_negative=False,
        test_table_id=test_id,
        model=best_model,
        threshold=0.5,
    )
    first_model_id = client.get_model_list(experiment.id)[0]['_id']
    pred_proba = client.batch_predict(
        pred_df=train_df,
        experiment_id=experiment.id,
        model_id=first_model_id)

    assert predict.attributes["status"] == "done"
    assert isinstance(predict.get_predict_df(), pd.DataFrame)
    assert isinstance(pred_proba, pd.DataFrame)
    assert predict.attributes["model_id"] == best_model.model_id
    assert predict.attributes["table_id"] == test_id

def test_train_and_predict_titanic_with_sep_holdout(client):
    print("---From test iid with separate holdout---")
    current_path = os.path.dirname(os.path.abspath(__file__))

    train_file_path = "data/train.csv"
    train_file = open(train_file_path, "rb")
    train_id = client.upload(train_file, "train_file")
    assert train_id is not None

    test_file_path = "data/test.csv"
    test_file = open(test_file_path, "rb")
    test_id = client.upload(test_file, "test_file")
    assert test_id is not None
    assert isinstance(client.get_table_list(), List)

    client.update_table(table_id=train_id,
                        updated_column='Pclass',
                        updated_type= DataType.categorical.value)
    
    exp_name = "exp_test_iid_with_separate_holdout"
    experiment = client.train_iid(
        experiment_name=exp_name,
        experiment_table_id=train_id,
        target="Survived",
        evaluator=ClassificationMetric.AUC,
        custom_column_types={
            "Pclass": DataType.categorical,
            "Parch": DataType.categorical,
        },
        algos=["GLM", "GBM", IIDAlgorithms.DRF, IIDAlgorithms.XGBoost],
        holdout_table_id = train_id,
        holdout_percentage = 10
    )

    assert experiment.status == "done"
    assert isinstance(experiment.get_model_list(), List)

    best_model = experiment.get_best_model()

    predict = client.predict_iid(
        keep_columns=[],
        non_negative=False,
        test_table_id=test_id,
        model=best_model,
        threshold=0.5,
    )

    assert predict.attributes["status"] == "done"
    assert isinstance(predict.get_predict_df(), pd.DataFrame)
    assert predict.attributes["model_id"] == best_model.model_id
    assert predict.attributes["table_id"] == test_id