variable "arn_role_lambda" {
  description = "arn of the role for lambda function"
  type        = string
}

variable "db_password" {
  description = "password for the RDS instance"
  type        = string
}

variable "profile" {
  description = "AWS profile to use"
  type        = string
}



variable "path_to_dockerfile_extract" {
  description = "Path to the Dockerfile for the extract lambda function"
  type        = string
  
}


variable "path_to_dockerfile_validation" {
  description = "Path to the Dockerfile for the validation lambda function"
  type        = string
  
}

variable "path_to_dockerfile_transformation" {
  description = "Path to the Dockerfile for the transformation lambda function"
  type        = string
  
}

variable "path_to_dockerfile_load" {
  description = "Path to the Dockerfile for the load lambda function"
  type        = string
  
}

variable "path_to_dockerfile_log" {
  description = "Path to the Dockerfile for the log lambda function"
  type        = string
  
}

variable "repo_portus" {
  description = "Name of the repository in Portus"
  type        = string
}

variable "region" {
  description = "AWS region to deploy resources"
  type        = string
  
}

variable "path_to_dockerfile_pgvector" {
  description = "Path to the Dockerfile for the pgvector initialization lambda function"
  type        = string
  
}

variable "arn_step_functions" {
  description = "ARN of the Step Functions role"
  type        = string
  
}

variable "path_to_dockerfile_silver2gold" {
  description = "Image uri silver2gold"
  type = string
  
}

variable "event_bridge_arn" {
  description = "arn event bridge"
  type=string
  
}

variable "path_to_dockerfile_inference" {
  description = "Path to the Dockerfile for the inference JSON lambda function"
  type        = string
  
}

variable "path_to_dockerfile_query" {
  description = "Path to the Dockerfile for the query lambda function"
  type        = string
  
}

variable "path_to_dockerfile_output" {
  description = "Path to the Dockerfile for the output evaluator lambda function"
  type        = string
  
}

variable "iam_profile" {
  description = "IAM profile for Dbeaver connection"
  type        = string
}