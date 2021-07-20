import uuid

import cv2
import uvicorn
from fastapi import File
from fastapi import FastAPI
from fastapi import UploadFile
import numpy as np
from PIL import Image


app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome from the API"}


@app.post("/windturbines/{cog}")
def get_windturbines(cog: str):
    return {"cog": cog}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
