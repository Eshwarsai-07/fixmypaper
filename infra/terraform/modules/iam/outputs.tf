output "api_role_arn" {
  value = aws_iam_role.api_role.arn
}

output "worker_role_arn" {
  value = aws_iam_role.worker_role.arn
}

output "eks_cluster_role_arn" {
  value = aws_iam_role.eks_cluster.arn
}

output "eks_node_role_arn" {
  value = aws_iam_role.eks_nodes.arn
}

output "fargate_pod_execution_role_arn" {
  value = aws_iam_role.fargate_pod_execution.arn
}
