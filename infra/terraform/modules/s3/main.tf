resource "aws_s3_bucket" "main" {
  bucket = var.bucket_name
  tags = {
    Name = "${var.project_name}-s3"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    id      = "DeleteOldFiles"
    status  = "Enabled"
    expiration {
      days = 7
    }
  }
}

resource "aws_s3_bucket_public_access_block" "main" {
  bucket = aws_s3_bucket.main.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
