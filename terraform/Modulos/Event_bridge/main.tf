# Regla EventBridge que escucha eventos ObjectCreated en tu bucket
resource "aws_cloudwatch_event_rule" "s3_object_created" {
  name        = "s3-object-created-trigger"
  description = "Trigger Step Function when object created in S3"

  event_pattern = jsonencode({
    source = ["aws.s3"],
    detail_type = ["Object Created"],
    resources = [
    var.arn_bucket
  ]
  })
}

# Target: conectar regla con Step Function
resource "aws_cloudwatch_event_target" "trigger_step_function" {
  rule      = aws_cloudwatch_event_rule.s3_object_created.name
  arn       = var.target_arn_step_functions
  role_arn  = var.event_bridge_arn
}

