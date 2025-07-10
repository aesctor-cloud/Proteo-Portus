resource "null_resource" "docker_build_and_push" {
  triggers = {
    always_run = "${timestamp()}"
  }    
  provisioner "local-exec" {
    command = <<EOT
      aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin ${var.repository_url} && docker build -t ${var.repository_name}-${var.image_tag} ${var.path_to_dockerfile} && docker tag ${var.repository_name}-${var.image_tag}:latest ${var.repository_url}:${var.image_tag} && docker push ${var.repository_url}:${var.image_tag}
    EOT
  }


}

data "aws_ecr_image" "my_image" {
  repository_name = var.repository_name
  image_tag       = var.image_tag
  depends_on      = [null_resource.docker_build_and_push]
}