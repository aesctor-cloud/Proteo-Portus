variable "arn_role_lambda" {
  description = "arn of the role for lambda function"
  type        = string
}

variable "subnet_a_id" {
  description = "Subred privada A"
  type        = string
}

variable "subnet_b_id" {
  description = "Subred privada B"
  type        = string
}

variable "security_group_lambda" {
  description = "Security group for lambda function"
  type        = string
}

variable "hostname_rds" {
  description = "Password for the RDS instance"
  type        = string
}

variable "port_rds" {
  description = "Port of the RDS instance"
  type        = number
}

variable "username_rds" {
  description = "Username for the RDS instance"
  type        = string
}

variable "password_rds" {
  description = "Password for the RDS instance"
  type        = string
}

variable "database_name" {
  description = "Name of the database in the RDS instance"
  type        = string
}


variable "image_uri_extract" {
  description = "URI of the Docker image for the Lambda function"
  type        = string
  
}

variable "image_uri_validation" {
  description = "URI of the Docker image for the validation Lambda function"
  type        = string
  
}

variable "image_uri_transformation" {
  description = "URI of the Docker image for the transformation Lambda function"
  type        = string
  
}

variable "image_uri_load" {
  description = "URI of the Docker image for the load Lambda function"
  type        = string
  
}

variable "image_uri_log" {
  description = "URI of the Docker image for the log Lambda function"
  type        = string
  
}

variable "image_uri_pgvector" {
  description = "Image of the Lambda function to initialize pgvector"
  type        = string
}

variable "image_uri_silver2gold" {
  description = "Image of the Lambda function silvergold"
  type=string
  
}

variable "image_uri_inference" {
  description = "URI of the Docker image for the inference JSON Lambda function"
  type        = string
  
}

variable "image_uri_query" {
  description = "URI of the Docker image for the query Lambda function"
  type        = string
  
}

variable "image_uri_output" {
  description = "URI of the Docker image for the output evaluator Lambda function"
  type        = string

}