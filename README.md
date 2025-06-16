# s3-exporter

docker run -p 9101:9101 --rm \
  -e S3_REGION="ap-southeast-2" \
  -e S3_ACCESS_KEY="xxx" \
  -e S3_SECRET_KEY="xxx" \
  -e S3_GLOBAL_BUCKET="s3-odoo-database-backup" \
  -e S3_GLOBAL_PREFIX="production/" \
  -e S3_FILE_0_KEY="path1/file1.zip" \
  -e S3_FILE_1_KEY="path2/file2.zip" \
  -e S3_FILE_2_BUCKET="another-bucket" \
  -e S3_FILE_2_KEY="special/file.zip" \
  -e EXPORTER_PORT="9101" \
  -e CHECK_INTERVAL_SECONDS="300" \
  nikiakbar/custom-s3-exporter
