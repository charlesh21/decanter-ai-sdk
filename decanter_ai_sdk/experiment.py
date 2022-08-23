from unicodedata import category
from attr import attributes
from pydantic import BaseModel, Field
from typing import Any, List, Dict, Optional, Union
from decanter_ai_sdk.enums.evaluators import ClassificationMetric, RegressionMetric
from decanter_ai_sdk.model import Model
import sys


class Experiment(BaseModel):
    algos: List[str]
    attributes: Dict
    bagel_id: str
    best_model: str
    best_model_id: str
    best_score: float
    category: str
    company_id: str
    completed_at: str
    corex_models: List[str]
    created_at: str
    created_by: Any
    data_id: str
    error: Dict[str, str]
    feature_types: List[Dict[str, str]]
    features: List[str]
    forecast_column: Optional[str]
    forecast_exogeneous_columns: List[str] = []
    forecast_time_group_columns: List[str] = []
    gp_table_id: str
    holdout: Dict[str, str]
    holdout_percentage: float
    is_binary_classification: bool
    is_favorited: bool
    is_forecast: bool
    is_starred: bool
    max_model: int
    name: str
    nfold: int
    preprocessing: Dict[str, str]
    progress: float
    progress_message: str
    project_id: str
    recommendations: List[Dict]
    seed: int
    stacked_ensemble: bool
    started_at: str
    status: str
    stopping_metric: str
    target: str
    target_type: str
    task_id: str
    timeseriesValues: Dict
    tolerance: float
    train_table: Dict
    updated_at: str
    validation_percentage: float
    id: str = Field(..., alias="_id")
    """
    Experiment class returned by training actions.
    """

    def get_best_model(self) -> Model:
        """
        Return best model in the experiment.

        Returns:
            (:class: `~decanter_ai_sdk.web_api.model.Model`)
        """

        return Model(
            model_id=self.best_model_id,
            model_name=self.best_model,
            metrics_score=self.attributes[self.best_model]["cv_averages"],
            experiment_id=self.id,
            experiment_name=self.name,
            attributes=self.attributes[self.best_model],
        )

    def get_best_model_by_metric(
        self, metric: Union[ClassificationMetric, RegressionMetric]
    ) -> Model:
        """
        Return best model by input metric.

        Parameters:
        ----------
            metric(`~decanter_ai_sdk.enums.evaluators.ClassificationMetric`, `decanter_ai_sdk.enums.evaluators.RegressionMetric`)
                Standard metric.

        Returns:
        ----------
            (`~decanter_ai_sdk.web_api.model.Model`)
                Best model selected by input metric.
        """
        if (
            metric == ClassificationMetric.AUC
            or metric == RegressionMetric.R2
            or metric == ClassificationMetric.LIFT_TOP_GROUP
        ):
            score = None
            for attr in self.attributes:
                if (
                    score == None
                    or float(self.attributes[attr]["cv_averages"][metric.value]) > score
                ):
                    score = float(self.attributes[attr]["cv_averages"][metric.value])
                    result = Model(
                        model_id=self.attributes[attr]["model_id"],
                        model_name=attr,
                        metrics_score=self.attributes[attr]["cv_averages"],
                        experiment_id=self.id,
                        experiment_name=self.name,
                        attributes=self.attributes[attr],
                    )
        else:
            score = None
            for attr in self.attributes:
                if (
                    score == None
                    or float(self.attributes[attr]["cv_averages"][metric.value]) < score
                ):
                    score = float(self.attributes[attr]["cv_averages"][metric.value])
                    result = Model(
                        model_id=self.attributes[attr]["model_id"],
                        model_name=attr,
                        metrics_score=self.attributes[attr]["cv_averages"],
                        experiment_id=self.id,
                        experiment_name=self.name,
                        attributes=self.attributes[attr],
                    )

        return result

    def get_model_list(self) -> List[Model]:
        """
        Return List of models generated by the experiment.

        Returns:
        ----------
            (List[`decanter.web_api.model.Model`]): List of models.
        """
        list = []

        for attr in self.attributes:

            list.append(
                Model(
                    model_id=self.attributes[attr]["model_id"],
                    model_name=attr,
                    metrics_score=self.attributes[attr]["cv_averages"],
                    experiment_id=self.id,
                    experiment_name=self.name,
                    attributes=self.attributes[attr],
                )
            )

        return list

    def experiment_info(self) -> Dict:
        """
        Return experiment information.

        Returns:
        ----------
            (Dict)Dictionary of experiment information.
        """
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }
