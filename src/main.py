import geojson
import uvicorn
from celery.result import AsyncResult
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from geojson_pydantic.features import Feature, FeatureCollection
from geojson_pydantic.geometries import Polygon

from src.pydantic_models import LaunchPredictionPayload, MlModelsConfig
from src.utils import load_ml_config, validate_model_by_id
from src.worker import create_task

# from src.inference import save_tiles_for_zoom
# from aiocogeo import COGReader


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
    available_models = validate_model_by_id(model_id)

    return [model for model in available_models.models if model.id == model_id][0]


@app.post("/predict", status_code=201)
def launch_prediction(payload: LaunchPredictionPayload):
    model_id = payload.model_id
    _ = validate_model_by_id(model_id)

    if not isinstance(payload.aoi.geometry, Polygon):
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="Currently only single feature of type Polygon supported",
        )

    task_type = 2
    task = create_task.delay(int(task_type))
    return JSONResponse({"prediction_task_id": task.id})


@app.get("/predict/{prediction_task_id}")
def get_prediction_status(prediction_task_id):
    task_result = AsyncResult(prediction_task_id)

    ## TODO: remove this later - only to ensure the desired response
    random_poly = geojson.utils.generate_random("Polygon")
    fc = FeatureCollection(features=[Feature(geometry=random_poly)])

    result = {
        "task_id": prediction_task_id,
        "task_status": task_result.status,
        "task_result": fc.dict(),
    }
    return JSONResponse(result)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
