FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run both the FastAPI server and the multiprocessing worker
CMD ["sh", "-c", "python worker.py & uvicorn main:app --host 0.0.0.0 --port 8000"]
