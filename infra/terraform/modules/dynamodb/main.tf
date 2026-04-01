resource "aws_dynamodb_table" "jobs" {
  name             = "${var.project_name}-jobs"
  billing_mode     = "PAY_PER_REQUEST"
  hash_key         = "job_id"
  range_key        = "user_id"

  attribute {
    name = "job_id"
    type = "S"
  }

  attribute {
    name = "user_id"
    type = "S"
  }

  # Idempotency Filter GSI
  attribute {
    name = "idempotency_key"
    type = "S"
  }

  global_secondary_index {
    name               = "IdempotencyIndex"
    hash_key           = "idempotency_key"
    projection_type    = "ALL"
  }

  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }

  tags = {
    Name = "${var.project_name}-jobs"
  }
}

resource "aws_dynamodb_table" "formats" {
  name         = "${var.project_name}-formats"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "format_id"

  attribute {
    name = "format_id"
    type = "S"
  }

  tags = {
    Name = "${var.project_name}-formats"
  }
}
