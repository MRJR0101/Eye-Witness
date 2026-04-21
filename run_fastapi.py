from fastapi import FastAPI
import uvicorn
from examples.fastapi_app.main import create_app

app = create_app(FastAPI())

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
