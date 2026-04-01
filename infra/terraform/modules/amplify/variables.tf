variable "project_name" {
  description = "Project name"
  type        = string
}

variable "github_repository" {
  description = "GitHub repository URL"
  type        = string
  default     = "https://github.com/Eshwarsai-07/fixmypaper"
}

variable "github_access_token" {
  description = "GitHub Personal Access Token (PAT)"
  type        = string
  sensitive   = true
}

variable "branch_name" {
  description = "GitHub branch to deploy"
  type        = string
  default     = "main"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

# Backend Environment Variables
variable "s3_bucket_name" {
  type = string
}

variable "dynamodb_table_jobs" {
  type = string
}

variable "dynamodb_table_formats" {
  type = string
}

variable "step_function_arn" {
  type = string
}

variable "frontend_access_key_id" {
  type = string
}

variable "frontend_secret_access_key" {
  type      = string
  sensitive = true
}
