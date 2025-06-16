import boto3
import os
import time
from datetime import datetime, timezone
from prometheus_client import start_http_server, Gauge

# Define Prometheus metric
last_modified_metric = Gauge(
    's3_object_last_modified_timestamp_seconds',
    'Last modified time of S3 object',
    ['bucket', 'key']
)

def load_files_from_env():
    """Load file list from numbered environment variables like S3_FILE_0_BUCKET, S3_FILE_0_KEY"""
    files = []
    i = 0
    while True:
        bucket = os.getenv(f'S3_FILE_{i}_BUCKET')
        key = os.getenv(f'S3_FILE_{i}_KEY')
        if not bucket or not key:
            break
        files.append({'bucket': bucket, 'key': key})
        i += 1
    return files

def load_config_from_env():
    """Load configuration from environment variables"""
    return {
        'endpoint_url': os.getenv('S3_ENDPOINT_URL'),
        'region': os.getenv('S3_REGION', 'us-east-1'),
        'access_key': os.getenv('S3_ACCESS_KEY'),
        'secret_key': os.getenv('S3_SECRET_KEY'),
        'files': load_files_from_env()
    }

def create_s3_client(cfg):
    """Create a boto3 S3 client"""
    return boto3.client(
        's3',
        endpoint_url=cfg['endpoint_url'],
        region_name=cfg['region'],
        aws_access_key_id=cfg['access_key'],
        aws_secret_access_key=cfg['secret_key']
    )

def update_metrics(s3, files):
    """Update Prometheus metrics for each monitored file"""
    for file in files:
        bucket = file['bucket']
        key = file['key']
        try:
            response = s3.head_object(Bucket=bucket, Key=key)
            last_modified = response['LastModified'].replace(tzinfo=timezone.utc).timestamp()
            last_modified_metric.labels(bucket=bucket, key=key).set(last_modified)
            print(f"✅ Updated: {bucket}/{key} -> {last_modified}")
        except Exception as e:
            print(f"❌ Error checking {bucket}/{key}: {e}")

def main():
    config = load_config_from_env()
    s3 = create_s3_client(config)
    files = config['files']

    if not files:
        print("⚠️ No files configured. Exiting.")
        return

    port = int(os.getenv('EXPORTER_PORT', '9101'))
    print(f"📡 Starting Prometheus exporter on port {port}")
    start_http_server(port)

    interval = int(os.getenv('CHECK_INTERVAL_SECONDS', '300'))

    while True:
        update_metrics(s3, files)
        time.sleep(interval)

if __name__ == '__main__':
    main()
