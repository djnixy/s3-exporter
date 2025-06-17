import boto3
import os
import time
from datetime import datetime, timezone
from prometheus_client import start_http_server, Gauge

# Prometheus metric
last_modified_metric = Gauge(
    's3_object_last_modified_timestamp_seconds',
    'Last modified time of S3 object',
    ['bucket', 'key']
)

def load_files():
    files = []
    i = 0
    while True:
        key = os.getenv(f'FILE_{i}_KEY')
        if not key:
            break
        bucket = os.getenv(f'FILE_{i}_BUCKET')  # optional override
        files.append({'key': key, 'bucket': bucket})
        i += 1
    return files

def load_config_from_env():
    return {
        'global': {
            'bucket': os.getenv('GLOBAL_BUCKET'),
            'prefix': os.getenv('GLOBAL_PREFIX', ''),
            's3': {
                'endpoint_url': os.getenv('GLOBAL_S3_ENDPOINT_URL'),
                'region': os.getenv('GLOBAL_S3_REGION', 'us-east-1'),
            },
            'credentials': {
                'access_key': os.getenv('GLOBAL_SECRET_KEYS_ACCESS_KEY'),
                'secret_key': os.getenv('GLOBAL_SECRET_KEYS_SECRET_KEY'),
            }
        },
        'exporter': {
            'port': int(os.getenv('EXPORTER_PORT', 9101)),
            'check_interval': int(os.getenv('EXPORTER_CHECK_INTERVAL_SECONDS', 300)),
        },
        'files': load_files()
    }

def create_s3_client(global_cfg):
    creds = global_cfg['credentials']
    return boto3.client(
        's3',
        endpoint_url=global_cfg['s3']['endpoint_url'],
        region_name=global_cfg['s3']['region'],
        aws_access_key_id=creds['access_key'],
        aws_secret_access_key=creds['secret_key']
    )

def update_metrics(s3, files, default_bucket, prefix):
    for file in files:
        bucket = file.get('bucket') or default_bucket
        key = f"{prefix}{file['key']}"
        try:
            response = s3.head_object(Bucket=bucket, Key=key)
            last_modified = response['LastModified'].replace(tzinfo=timezone.utc).timestamp()
            last_modified_metric.labels(bucket=bucket, key=key).set(last_modified)
            print(f"✅ {bucket}/{key} -> {last_modified}")
        except Exception as e:
            print(f"❌ Failed: {bucket}/{key}: {e}")

def main():
    cfg = load_config_from_env()
    s3 = create_s3_client(cfg['global'])
    files = cfg['files']
    if not files:
        print("⚠️ No files configured.")
        return

    port = cfg['exporter']['port']
    interval = cfg['exporter']['check_interval']
    default_bucket = cfg['global']['bucket']
    prefix = cfg['global']['prefix']

    print(f"📡 Exporter running on port {port}")
    start_http_server(port)

    while True:
        update_metrics(s3, files, default_bucket, prefix)
        time.sleep(interval)

if __name__ == "__main__":
    main()
