variable "project_name" {
  type = string
}

variable "sqs_queue_name" {
  type = string
}

variable "sqs_backlog_threshold" {
  type    = number
  default = 100
}

variable "sfn_arn" {
  type = string
}

variable "aws_region" {
  type = string
}
