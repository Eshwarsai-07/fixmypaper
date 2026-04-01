output "table_name" {
  value = aws_dynamodb_table.jobs.name
}

output "table_arn" {
  value = aws_dynamodb_table.jobs.arn
}

output "stream_arn" {
  value = aws_dynamodb_table.jobs.stream_arn
}
