from typing import List, Optional

from pydantic import BaseModel


class ModelMetadata(BaseModel):
    name: str
    id: int
    prediction_type: str
    learning_approach: str
    architecture: str
    description: Optional[str]
    gsd_per_pixel: str


class MlModelsConfig(BaseModel):
    models: List[ModelMetadata]
