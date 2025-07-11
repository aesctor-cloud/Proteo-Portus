variable "repository_name" {
  description = "Name of the ECR repository"
  type        = string
}

variable "repository_url" {
  description = "URL of the ECR repository"
  type        = string
}

variable "path_to_dockerfile" {
  description = "Path to the Dockerfile for the ECR image"
  type        = string
}

variable "image_tag" {
  description = "Tag for the Docker image"
  type        = string
}