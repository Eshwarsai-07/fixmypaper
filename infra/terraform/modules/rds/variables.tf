variable "project_name" {
  description = "Project name"
  type        = string
}

variable "db_name" {
  description = "RDS database name"
  type        = string
}

variable "db_user" {
  description = "RDS database user"
  type        = string
}

variable "db_password" {
  description = "RDS database password"
  type        = string
  sensitive   = true
}

variable "vpc_id" {
  description = "VPC id"
  type        = string
}

variable "subnet_ids" {
  description = "VPC private subnet ids"
  type        = list(string)
}

variable "vpc_sg_id" {
  description = "VPC security group id"
  type        = string
}
