resource "aws_cloudwatch_metric_alarm" "sqs_backlog" {
  alarm_name          = "${var.project_name}-sqs-backlog"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = "60"
  statistic           = "Average"
  threshold           = var.sqs_backlog_threshold
  alarm_description   = "SQS backlog spike detected - potential worker bottleneck"
  dimensions = {
    QueueName = var.sqs_queue_name
  }
}

resource "aws_cloudwatch_metric_alarm" "sfn_failure" {
  alarm_name          = "${var.project_name}-sfn-failure"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ExecutionsFailed"
  namespace           = "AWS/States"
  period              = "60"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "Step Function execution failure detected"
  dimensions = {
    StateMachineArn = var.sfn_arn
  }
}

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project_name}-health"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", var.sqs_queue_name]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "SQS Queue Depth"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/States", "ExecutionsFailed", "StateMachineArn", var.sfn_arn]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "Step Function Failures"
        }
      }
    ]
  })
}
