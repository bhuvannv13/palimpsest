FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends tesseract-ocr \
    tesseract-ocr-grc tesseract-ocr-lat tesseract-ocr-heb tesseract-ocr-san && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -e ".[all]"
EXPOSE 7860
ENV GRADIO_SERVER_NAME=0.0.0.0
CMD ["palimpsest", "app"]
