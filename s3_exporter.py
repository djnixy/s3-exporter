import boto3
import yaml
import time
from prometheus_client import start_http_server, Gauge
from datetime import datetime, timezone

last_modified_metric = Gauge(
    's3_object_last_modified_timestamp_seconds',
    'Last modified time of S3 object',
    ['bucket', 'key']
)

def load_config(path='config.yaml'):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def create_s3_client(config):
    s3_config = config['s3']
    session = boto3.session.Session()

    return session.client(
        's3',
        endpoint_url=s3_config.get('endpoint_url') or None,
        region_name=s3_config.get('region') or None,
        aws_access_key_id=s3_config['access_key'],
        aws_secret_access_key=s3_config['secret_key']
    )

def update_metrics(s3, files):
    for file in files:
        bucket = file['bucket']
        key = file['key']
        try:
            response = s3.head_object(Bucket=bucket, Key=key)
            last_modified = response['LastModified'].replace(tzinfo=timezone.utc).timestamp()
            last_modified_metric.labels(bucket=bucket, key=key).set(last_modified)
            print(f"Updated: {bucket}/{key} -> {last_modified}")
        except Exception as e:
            print(f"Error checking {bucket}/{key}: {e}")

def main():
    config = load_config()
    s3 = create_s3_client(config)
    files = config['files']

    port = 9101
    print(f"Starting Prometheus exporter on port {port}...")
    start_http_server(port)

    while True:
        update_metrics(s3, files)
        time.sleep(300)  # every 5 minutes

if __name__ == '__main__':
    main()
