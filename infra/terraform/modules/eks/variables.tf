variable "project_name" {
  description = "Project name"
  type        = string
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
}

variable "subnet_ids" {
  description = "VPC private subnet ids"
  type        = list(string)
}

variable "eks_role_arn" {
  description = "EKS cluster role arn"
  type        = string
}

variable "node_role_arn" {
  description = "EKS node role arn"
  type        = string
}
