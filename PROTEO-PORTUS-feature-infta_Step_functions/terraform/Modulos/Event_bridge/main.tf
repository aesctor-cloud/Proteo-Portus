# Regla EventBridge que escucha eventos ObjectCreated en tu bucket
resource "aws_cloudwatch_event_rule" "s3_object_created" {
  name        = "s3-object-created-trigger"
  description = "Trigger Step Function when object created in S3"

event_pattern = jsonencode({
  "source": ["aws.s3"],
  "detail-type": ["Object Created"]
})

}

# Target: conectar regla con Step Function
resource "aws_cloudwatch_event_target" "trigger_step_function" {
  rule      = aws_cloudwatch_event_rule.s3_object_created.name
  arn       = var.target_arn_step_functions
  role_arn  = var.event_bridge_arn

}

# Bucket S3 donde se guardarán los logs de CloudTrail
resource "aws_s3_bucket" "cloudtrail_logs" {
  bucket = "bucket-logs-trail-portus"
  tags = {
    name = "bucket logs trail portus"
    environment = "production"
  }
}

data "aws_caller_identity" "current" {}

resource "aws_s3_bucket_policy" "cloudtrail_logs_policy" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action = "s3:GetBucketAcl"
        Resource = "arn:aws:s3:::${aws_s3_bucket.cloudtrail_logs.id}"
      },
      {
        Sid = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action = "s3:PutObject"
        Resource = "arn:aws:s3:::${aws_s3_bucket.cloudtrail_logs.id}/AWSLogs/${data.aws_caller_identity.current.account_id}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
  depends_on = [aws_s3_bucket.cloudtrail_logs]

}


# Crear el CloudTrail
resource "aws_cloudtrail" "main" {
  name                          = "mi-cloudtrail"
  s3_bucket_name                = aws_s3_bucket.cloudtrail_logs.bucket
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_logging                = true

  # Activar eventos de datos para el bucket S3 de interés (por ejemplo, otro bucket que quieres monitorear)
  event_selector {
    read_write_type           = "All" 
    include_management_events = true

    data_resource {
      type   = "AWS::S3::Object"
      values = ["arn:aws:s3:::raw-bucket-proteo-energia/*"] # Bucket a monitorear
    }
  }
}


