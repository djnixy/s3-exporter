FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the exporter code
COPY s3_exporter.py config.yaml ./

EXPOSE 9101

CMD ["python", "s3_exporter.py"]