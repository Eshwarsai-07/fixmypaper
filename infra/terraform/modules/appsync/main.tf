resource "aws_appsync_graphql_api" "main" {
  name                = "${var.project_name}-api"
  authentication_type = "API_KEY"
  schema              = file("${path.module}/schema.graphql")
}

resource "aws_appsync_api_key" "main" {
  api_id = aws_appsync_graphql_api.main.id
}

resource "aws_appsync_datasource" "none" {
  api_id = aws_appsync_graphql_api.main.id
  name   = "NONE_DS"
  type   = "NONE"
}

resource "aws_appsync_resolver" "publish_update" {
  api_id      = aws_appsync_graphql_api.main.id
  field       = "publishJobUpdate"
  type        = "Mutation"
  data_source = aws_appsync_datasource.none.name

  request_template = <<EOF
{
  "version": "2017-02-28",
  "payload": $util.toJson($context.arguments)
}
EOF

  response_template = "$util.toJson($context.result)"
}
