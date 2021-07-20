import uvicorn
from aiocogeo import COGReader
from fastapi import FastAPI, HTTPException

from inference import save_tiles_for_zoom

app = FastAPI(debug=True)


@app.get("/")
def read_root():
    return {"message": "Welcome from the API"}


@app.get("/windturbines/cog")
async def get_windturbines(url: str):
    print(url)
    if url == "":
        raise HTTPException(status_code=400, detail="cog url is needed")

    async with COGReader(url) as cog:

        fc = await save_tiles_for_zoom(cog, 17)

    return fc


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
