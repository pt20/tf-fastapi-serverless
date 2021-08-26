import os

import yaml
from fastapi import status
from fastapi.exceptions import HTTPException

from src.pydantic_models import MlModelsConfig

file_path = os.path.join(os.path.dirname(__file__), "ml-config.yaml")


def load_ml_config() -> MlModelsConfig:
    """
    loads the model yaml config file into pydantic model

    Returns:
        MlModelsConfig: Pydantic model corresponding to model metadata
    """
    with open(file_path, "r") as stream:
        ml_config = yaml.safe_load(stream)

    return MlModelsConfig(**ml_config)


def validate_model_by_id(model_id: int) -> MlModelsConfig:
    """
    Function to validate if the prediction requested for model is in the config

    Args:
        model_id (int): model_id listed in the ml-config.yaml

    Raises:
        HTTPException: 404 - model not found

    Returns:
        MlModelsConfig: Pydantic model corresponding to model metadata
    """
    available_models = load_ml_config()
    ids = [model.id for model in available_models.models]

    if model_id not in ids:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Model not found")

    return available_models
