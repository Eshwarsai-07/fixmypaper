output "vpc_id" {
  value = module.vpc.vpc_id
}

output "eks_cluster_name" {
  value = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "ecr_repository_url_api" {
  value = module.ecr.api_repository_url
}

output "ecr_repository_url_worker" {
  value = module.ecr.worker_repository_url
}

output "cognito_user_pool_id" {
  value = module.cognito.user_pool_id
}

output "cognito_client_id" {
  value = module.cognito.client_id
}

output "appsync_graphql_url" {
  value = module.appsync.graphql_url
}

output "s3_bucket_name" {
  value = module.s3.bucket_name
}



output "standard_sfn_arn" {
  value = module.step_functions.standard_sfn_arn
}
