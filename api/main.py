from fastapi import FastAPI
import logging

logging.basicConfig(
    level=logging.ERROR,
    format="%(levelname)s | %(name)s | %(message)s"
)
app = FastAPI()

@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}

