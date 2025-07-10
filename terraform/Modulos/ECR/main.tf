resource "aws_ecr_repository" "repo-portus" {
  name = var.repository_name
  force_delete = true
  tags = {
    Name = "Portus ECR Repository"
  }
}


