import uvicorn
from aiocogeo import COGReader
from fastapi import FastAPI, HTTPException

from response_models import MlModelsConfig

# from src.inference import save_tiles_for_zoom
from utils import load_ml_config

app = FastAPI(debug=True)


@app.get("/")
def read_root():
    return {"message": "Sometimes the wheel turns slowly, but it turns."}


## deprecated in favour of AOI
# @app.get("/windturbines/cog")
# async def get_windturbines(url: str):
#     if url == "":
#         raise HTTPException(status_code=400, detail="cog url is required")

#     async with COGReader(url) as cog:

#         fc = await save_tiles_for_zoom(cog, 17)

#     return fc


@app.get("/models")
def list_models() -> MlModelsConfig:
    return load_ml_config()


## TODO: maybe use a uuid or something for model_id in the future
@app.get("/models/{model_id}", description="Get a model metadata by id")
def get_model_by_id(model_id: int) -> MlModelsConfig:
    available_models = load_ml_config()
    ids = [model.id for model in available_models.models]

    if model_id not in ids:
        raise HTTPException(404, detail="Model not found")

    return [model for model in available_models.models if model.id == model_id][0]


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
