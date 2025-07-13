variable "instance_name" {
  description = "Nombre de la instancia"
  type        = string
  
}
variable "vpc_id" {
  description = "ID de la VPC donde se desplegará la instancia"
  type        = string
  
}

variable "rds_sg_id" {
  description = "ID del grupo de seguridad de RDS"
  type        = string
}

variable "private_subnet_id" {
  description = "ID de la subred privada donde se desplegará la instancia"
  type        = string
  
}

variable "iam_profile" {
  description = "Perfil de IAM asociado a la instancia"
  type        = string
  
}