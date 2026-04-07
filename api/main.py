from contextlib import asynccontextmanager

from fastapi import FastAPI
from db import Base, engine
import models
from models import Agent
import logging

logging.basicConfig(
    level=logging.ERROR,
    format="%(levelname)s | %(name)s | %(message)s"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
app = FastAPI(lifespan=lifespan)

@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}

