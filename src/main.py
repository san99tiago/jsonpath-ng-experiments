from fastapi import FastAPI
from .mapper.mapper import Mapper
from .mapper.validator import Validator


app = FastAPI(
    description="Simple FastAPI server for local JSON validations and mappings",
    contact={"Santiago Garcia Arango": "santiago.garcia1999@hotmail.com"},
    title="Simple FastAPI for JSON experiments",
    version="0.0.1",
)


@app.get("/")
async def root():
    return {"message": "Hello by Santi!"}


@app.get("/status")
async def get_status():
    return {"status": "OK"}


@app.patch("/quotes")
async def patch_payload(payload: dict):
    print("Starting patch quotes processing...")

    validator = Validator()
    payload_validation_result = validator.validate_payload(payload)
    if payload_validation_result is True:
        mapper = Mapper(payload)
        return mapper.convert_payload()
    return payload_validation_result
