import pandas as pd
from fastapi import FastAPI, UploadFile, File,  Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List
from fastapi.encoders import jsonable_encoder
import sklearn
import numpy as np
from fastapi.responses import StreamingResponse
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from auth.users import auth_backend, current_active_user, fastapi_users
from auth.schemas import UserCreate, UserRead #, UserUpdate
from auth.db import User, create_db_and_tables
from datetime import datetime
from link.router import router as link_router
#from tasks.router import router as tasks_router
from redis import asyncio as aioredis
#from fastapi_cache import FastAPICache
#from fastapi_cache.backends.redis import RedisBackend
import uvicorn
from typing import Optional


app = FastAPI()


app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(link_router)

@app.get("/protected-route")
def protected_route(user: User = Depends(current_active_user)):
    return f"Hello, {user.email}"


@app.get("/unprotected-route")
def unprotected_route():
    return f"Hello, anonym"

@app.get("/items")
async def read_items(user: Optional[User] = Depends(fastapi_users.current_user(optional=True))):  # ИЗМЕНЕНО: Используем fastapi_users.current_user(optional=True)
    if user:
        return {"message": f"Hello, {user.email}!"}
    else:
        return {"message": "Hello, anonym!"}



if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="0.0.0.0", log_level="info")


# uvicorn main:app --reload --port 8000
# app - приложение FastAPI()
# main - название файла




