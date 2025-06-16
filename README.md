# 📦 S3 File Timestamp Exporter for Prometheus

This exporter checks the **last modified time** of objects in an S3 (or S3-compatible) bucket and exposes it as a Prometheus metric:

s3_object_last_modified_timestamp_seconds{bucket="...", key="..."} <unix_timestamp>



---

## ✅ Features

- Works with **AWS S3**, **DigitalOcean Spaces**, **MinIO**, and other S3-compatible services
- No configuration file needed – just use environment variables
- Docker-ready and minimal footprint
- Suitable for cron-style freshness alerts

---

## 🔧 Environment Variables

| Variable                        | Description                                      |
|--------------------------------|--------------------------------------------------|
| `S3_ENDPOINT_URL`              | S3 API endpoint (e.g., `https://s3.amazonaws.com`) |
| `S3_REGION`                    | AWS region (e.g., `ap-southeast-2`)              |
| `S3_ACCESS_KEY`                | S3 access key                                    |
| `S3_SECRET_KEY`                | S3 secret key                                    |
| `S3_GLOBAL_BUCKET`             | Optional default bucket for all files            |
| `S3_GLOBAL_PREFIX`             | Optional key prefix (e.g., `production/`)        |
| `S3_FILE_{N}_KEY`              | Key of object to monitor                         |
| `S3_FILE_{N}_BUCKET` (optional)| Specific bucket override per file                |
| `CHECK_INTERVAL_SECONDS`       | Interval between checks (default: `300`)         |
| `EXPORTER_PORT`                | Port to expose metrics (default: `9101`)         |

---

## 🐳 Docker Usage

### ✅ AWS S3 Example

```bash
docker run -p 9101:9101 --rm \
  -e S3_REGION="ap-southeast-2" \
  -e S3_ACCESS_KEY="your_aws_access_key" \
  -e S3_SECRET_KEY="your_aws_secret_key" \
  -e S3_GLOBAL_BUCKET="s3-odoo-database-backup" \
  -e S3_GLOBAL_PREFIX="production/" \
  -e S3_FILE_0_KEY="backups/db1.zip" \
  -e S3_FILE_1_KEY="backups/db2.zip" \
  nikiakbar/custom-s3-exporter
```
```✅ DigitalOcean Spaces Example
docker run -p 9101:9101 --rm \
  -e S3_ENDPOINT_URL="https://nyc3.digitaloceanspaces.com" \
  -e S3_REGION="nyc3" \
  -e S3_ACCESS_KEY="your_spaces_key" \
  -e S3_SECRET_KEY="your_spaces_secret" \
  -e S3_GLOBAL_BUCKET="my-space-name" \
  -e S3_FILE_0_KEY="backups/db1.zip" \
  -e S3_FILE_1_KEY="backups/db2.zip" \
  nikiakbar/custom-s3-exporter
```
📊 Prometheus Metrics
Example output:

```
# HELP s3_object_last_modified_timestamp_seconds Last modified time of S3 object
# TYPE s3_object_last_modified_timestamp_seconds gauge
s3_object_last_modified_timestamp_seconds{bucket="s3-odoo-database-backup",key="production/db.zip"} 1750071719.0
```
Sample alert in Prometheus (for files not updated in 1 day):

```
(time() - s3_object_last_modified_timestamp_seconds{key=~".*_latest.zip"}) > 86400
```