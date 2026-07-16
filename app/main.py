# pyrefly: ignore [missing-import]
from fastapi import FastAPI, Response, status
# pyrefly: ignore [missing-import]
from fastapi.responses import RedirectResponse, JSONResponse
# pyrefly: ignore [missing-import]
import uvicorn

app = FastAPI(title="DevOps College Project API")

# pyrefly: ignore [missing-import]
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

@app.get("/")
async def home():
        return {
            "message": "Version 1.0 - Stable Python FastAPI Production API" }

@app.get("/health")
async def health_check(response: Response):
    # Healthy endpoint returning HTTP 200
    response.status_code = status.HTTP_200_OK
    return {"status": "Healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)
