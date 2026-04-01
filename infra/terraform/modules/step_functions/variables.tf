variable "project_name" {
  description = "Project name"
  type        = string
}

variable "dynamodb_table_name" {
  description = "DynamoDB table name"
  type        = string
}

variable "sqs_queue_url" {
  description = "SQS queue URL"
  type        = string
}

variable "s3_bucket_name" {
  description = "S3 bucket for uploads"
  type        = string
}

variable "api_worker_url" {
  description = "The internal URL for the Grobid worker"
  type        = string
}

variable "subnet_ids" {
  description = "VPC private subnet ids"
  type        = list(string)
}

variable "security_group_id" {
  description = "Security group for Lambda"
  type        = string
}
