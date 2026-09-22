resource "aws_lambda_function" "healer" {
  filename = "lambda.zip"
  function_name = "auto-heal-bot"
  role = aws_iam_role.lambda_role.arn
  handler = "handler.handler"
  runtime = "python3.11"
  environment { variables = { SLACK_WEBHOOK = var.slack_webhook } }
}
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name = "high-cpu-api"
  metric_name = "CPUUtilization"
  namespace = "AWS/EKS"
  threshold = 80
  comparison_operator = "GreaterThanThreshold"
  period = 60
  evaluation_periods = 2
  alarm_actions = [aws_lambda_function.healer.arn]
}
variable "slack_webhook" {}
resource "aws_iam_role" "lambda_role" { name = "heal-bot-role" assume_role_policy = jsonencode({Version="2012-10-17",Statement=[{Effect="Allow",Principal={Service="lambda.amazonaws.com"},Action="sts:AssumeRole"}]}) }
