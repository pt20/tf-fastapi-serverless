import os

import yaml

from response_models import MlModelsConfig

file_path = os.path.join(os.path.dirname(__file__), "ml-config.yaml")


def load_ml_config() -> MlModelsConfig:
    with open(file_path, "r") as stream:
        ml_config = yaml.safe_load(stream)

    return MlModelsConfig(**ml_config)
