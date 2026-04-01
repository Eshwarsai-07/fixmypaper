output "graphql_url" {
  value = aws_appsync_graphql_api.main.uris["GRAPHQL"]
}

output "api_key" {
  value = aws_appsync_api_key.main.key
  sensitive = true
}
