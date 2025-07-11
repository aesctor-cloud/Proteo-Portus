output "image_uri" {
  value = "${var.repository_url}@${data.aws_ecr_image.my_image.image_digest}"
}

