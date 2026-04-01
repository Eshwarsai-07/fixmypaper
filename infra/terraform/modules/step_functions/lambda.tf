data "archive_file" "fallback_zip" {
  type        = "zip"
  source_file = "${path.module}/../../../../lambda/fallback_parser/main.py"
  output_path = "${path.module}/fallback_parser.zip"
}

resource "aws_iam_role" "lambda_fallback_role" {
  name = "${var.project_name}-lambda-fallback-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy" "lambda_fallback_policy" {
  name = "${var.project_name}-lambda-fallback-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "*" # Should be specific bucket
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:UpdateItem"
        ]
        Resource = "*" # Should be specific table
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_fallback_attach" {
  role       = aws_iam_role.lambda_fallback_role.name
  policy_arn = aws_iam_policy.lambda_fallback_policy.arn
}

resource "aws_lambda_function" "fallback" {
  filename         = data.archive_file.fallback_zip.output_path
  function_name    = "${var.project_name}-fallback-parser"
  role             = aws_iam_role.lambda_fallback_role.arn
  handler          = "main.lambda_handler"
  runtime          = "python3.11"
  source_code_hash = data.archive_file.fallback_zip.output_base64sha256

  environment {
    variables = {
      S3_BUCKET_NAME = var.s3_bucket_name
      DYNAMODB_TABLE = var.dynamodb_table_name
    }
  }
}

output "fallback_lambda_arn" {
  value = aws_lambda_function.fallback.arn
}
