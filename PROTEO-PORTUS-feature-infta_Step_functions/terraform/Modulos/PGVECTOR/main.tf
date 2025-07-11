resource "null_resource" "invoke_lambda_init_pgvector" {

  provisioner "local-exec" {
    command = <<EOT
      aws lambda invoke --function-name ${var.lambda_pgvector} --payload '{}' output.json
    EOT
  }
}