import os
# import requests
from fastapi import FastAPI, Response, Request, Header, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
import json
import signal
from dotenv import load_dotenv


load_dotenv()
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
async def ping():
    return {"message": "Server is Live"}

@app.post("/upload")
def upload(files: List[UploadFile] = File(...)):
    try:
        for file in files:
            contents = file.file.read()
            with open(f"out/{file.filename}", 'wb') as f:
                f.write(contents)
    except Exception as e:
        print(e)
        return {"message": "There was an error uploading the files"}
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {[file.filename for file in files]}"}

@app.get("/query")
async def query(q: str):
    print(q)

    # semantic router

    # openai

    # gaurd rails

    return {"message": "success"}

        

if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=8000)
