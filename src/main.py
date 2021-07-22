import uvicorn
from aiocogeo import COGReader
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from geojson import FeatureCollection

from models import User, UserInDB
from src.inference import save_tiles_for_zoom
from user import fake_hash_password, fake_users_db, get_current_active_user

app = FastAPI(debug=True)


@app.get("/")
def read_root():
    return {"message": "Welcome from the API"}


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/windturbines/cog")
async def get_windturbines(url: str):
    if url == "":
        raise HTTPException(status_code=400, detail="cog url is needed")

    print(url)
    async with COGReader(url) as cog:
        fc = save_tiles_for_zoom(cog, 18)

    return fc


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
