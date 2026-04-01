variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "fixmypaper"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}


variable "s3_bucket_name" {
  description = "S3 bucket for uploads"
  type        = string
}

variable "api_worker_url" {
  description = "API endpoint or ARN for Express parsing tasks"
  type        = string
}

variable "sqs_backlog_threshold" {
  description = "Threshold for SQS backlog alarm"
  type        = number
  default     = 100
}
