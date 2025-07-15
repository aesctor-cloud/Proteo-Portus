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

variable "vpc_cidr" {
  description = "CIDR block para la VPC"
  type        = string
}
 
variable "public_subnet_cidr" {
  description = "CIDR block para la subnet pública"
  type        = string
}
 
variable "instance_type" {
  description = "Tipo de instancia EC2"
  type        = string
}
 
variable "ami_id" {
  description = "AMI ID para la instancia EC2 (Ubuntu 22.04 LTS recomendado)"
  type        = string
}
 
variable "key_name" {
  description = "Nombre de la clave SSH para acceder a la instancia (opcional)"
  type        = string
  default     = ""
}
 
variable "github_repo_url" {
  description = "URL del repositorio GitHub a clonar"
  type        = string
}
 
variable "github_branch" {
  description = "Branch del repositorio GitHub a clonar"
  type        = string
  default     = "main"
}
 
variable "streamlit_folder" {
  description = "Carpeta dentro del repo donde está la app Streamlit"
  type        = string
}
 
variable "security_group_ingress_port" {
  description = "Puerto a abrir en el Security Group para Streamlit"
  type        = number
}
 
variable "assign_elastic_ip" {
  description = "¿Asignar Elastic IP a la instancia? (true/false)"
  type        = bool
  default     = true
}
 
variable "ec2_name" {
  description = "Nombre de la instancia EC2"
  type        = string
}

 
variable "tags" {
  description = "Tags para los recursos"
  type        = map(string)
  default     = {}
}
 
variable "public_key_path" {
  description = "Ruta al archivo de clave pública SSH"
  type        = string
}