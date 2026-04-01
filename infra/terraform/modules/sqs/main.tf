resource "aws_sqs_queue" "jobs_dlq" {
  name = "${var.project_name}-jobs-dlq"
  message_retention_seconds = 1209600 # 14 days
}

resource "aws_sqs_queue" "jobs" {
  name                      = "${var.project_name}-jobs"
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 345600 # 4 days
  receive_wait_time_seconds = 20
  visibility_timeout_seconds = 300 # Base 5-minute timeout (heartbeats will extend)

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.jobs_dlq.arn
    maxReceiveCount     = 3
  })

  tags = {
    Name = "${var.project_name}-jobs"
  }
}
