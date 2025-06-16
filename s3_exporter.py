import boto3
import os
import time
import yaml
from datetime import datetime, timezone
from prometheus_client import start_http_server, Gauge

# Prometheus metric
last_modified_metric = Gauge(
    's3_object_last_modified_timestamp_seconds',
    'Last modified time of S3 object',
    ['bucket', 'key']
)

def load_config_from_yaml(path='config.yaml'):
    with open(path, 'r') as f:
        cfg = yaml.safe_load(f)
    return cfg

def apply_global_config(cfg):
    global_bucket = cfg.get('global', {}).get('bucket')
    global_prefix = cfg.get('global', {}).get('prefix', '')

    for file in cfg.get('files', []):
        # Apply default bucket if missing
        if 'bucket' not in file and global_bucket:
            file['bucket'] = global_bucket

        # Apply prefix to key if it's not already prefixed
        if global_prefix and not file['key'].startswith(global_prefix):
            file['key'] = global_prefix + file['key']

    return cfg

def create_s3_client(cfg):
    return boto3.client(
        's3',
        endpoint_url=cfg.get('endpoint_url'),
        region_name=cfg.get('region', 'us-east-1'),
        aws_access_key_id=cfg.get('access_key'),
        aws_secret_access_key=cfg.get('secret_key')
    )

def update_metrics(s3, files):
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
    config_path = os.getenv('CONFIG_PATH', 'config.yaml')
    config = apply_global_config(load_config_from_yaml(config_path))

    s3 = create_s3_client(config['s3'])
    files = config.get('files', [])

    if not files:
        print("⚠️ No files configured. Exiting.")
        return

    port = config.get('exporter', {}).get('port', 9101)
    interval = config.get('exporter', {}).get('check_interval_seconds', 300)

    print(f"📡 Starting Prometheus exporter on port {port}")
    start_http_server(port)

    while True:
        update_metrics(s3, files)
        time.sleep(interval)

if __name__ == '__main__':
    main()
