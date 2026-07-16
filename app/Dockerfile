FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 3000
# Run using Uvicorn ASGI server on port 3000
CMD ["python3", "main.py"]
