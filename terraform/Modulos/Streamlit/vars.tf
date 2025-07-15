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

variable "iam_profile_streamlit" {
  description = "Perfil IAM para la instancia Streamlit"
  type        = string
  
}