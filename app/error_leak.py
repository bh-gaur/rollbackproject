from fastapi import FastAPI, Response, status
from prometheus_fastapi_instrumentator import Instrumentator
# import uvicorn

app = FastAPI(title="DevOps College Project API")


Instrumentator().instrument(app).expose(app, endpoint="/metrics")

@app.get("/")
async def read_root():
    return {"message": "Version 1.0 - Stable Python FastAPI Production API"}

@app.get("/health")
async def health_check(response: Response):
    # Intentionally breaking the application on the new feature branch
    response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return {"status": "Critical Internal Server Exception / Memory Leak Detected"}


# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)
