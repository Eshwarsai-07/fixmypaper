resource "aws_iam_role" "sfn_role" {
  name = "${var.project_name}-sfn-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "states.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "sfn_policy" {
  name = "${var.project_name}-sfn-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query"
        ]
        Resource = "*" # Should be scoped to the specific table ARN in real production
      },
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage"
        ]
        Resource = "*" # Should be scoped to the specific queue ARN
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = [
          aws_lambda_function.fallback.arn,
          aws_lambda_function.primary.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "states:StartExecution",
          "states:DescribeExecution",
          "states:StopExecution"
        ]
        Resource = "*" # Should be scoped to the Express ARN
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "sfn_attach" {
  role       = aws_iam_role.sfn_role.name
  policy_arn = aws_iam_policy.sfn_policy.arn
}

resource "aws_sfn_state_machine" "express" {
  name     = "${var.project_name}-parse-express"
  role_arn = aws_iam_role.sfn_role.arn
  type     = "EXPRESS"

  definition = templatefile("${path.module}/express_definition.json", {
    PRIMARY_LAMBDA_ARN = aws_lambda_function.primary.arn
  })
}

resource "aws_sfn_state_machine" "standard" {
  name     = "${var.project_name}-workflow-standard"
  role_arn = aws_iam_role.sfn_role.arn
  type     = "STANDARD"

  definition = templatefile("${path.module}/definition.json", {
    DYNAMODB_TABLE           = var.dynamodb_table_name
    SQS_QUEUE_URL            = var.sqs_queue_url
    LAMBDA_FALLBACK_ARN      = aws_lambda_function.fallback.arn
    EXPRESS_STATE_MACHINE_ARN = aws_sfn_state_machine.express.arn
  })
}

output "standard_sfn_arn" {
  value = aws_sfn_state_machine.standard.id
}
