import os
import logging
from typing import Union
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.v1.endpoints import auth, video
from app.core.logging_config import setup_logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError, HTTPException
from app.core.exception_handlers import validation_exception_handler, general_exception_handler, http_exception_handler

setup_logging() 


app = FastAPI()

origins = [
    "http://localhost:3000",  # Allow requests from the frontend (Vue.js)
    "http://localhost:8000",  # If you're using a different port for the API (adjust as needed)
    "http://localhost:80"
    "*",  # Allow all domains (be cautious with this in production)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allowed origins (for local development, add frontend URL)
    allow_credentials=True,  # Allow cookies and credentials in the requests
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Register global exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

@app.get("/")
def read_root():
    logging.info("Root endpoint accessed.")
    return {"message": "Hello World"}


# Mount the 'videos' folder to be publicly accessible under '/videos' endpoint
videos_dir = os.path.join(os.getcwd(), "videos")
app.mount("/videosList", StaticFiles(directory=videos_dir), name="videos")


app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(video.router, prefix="/videos", tags=["videos"])


@app.get("/error")
def trigger_error():
    raise ValueError("This is a test error!")

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}
