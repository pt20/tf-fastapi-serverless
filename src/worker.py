import os

from celery import Celery

from src.inference import run_prediction_for_aoi

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get(
    "CELERY_RESULT_BACKEND", "redis://localhost:6379"
)

## TODO: Bring prediction business here


@celery.task(name="create_task")
def create_task(aoi, uri):
    fc = run_prediction_for_aoi(aoi, uri)

    return fc.dict()
