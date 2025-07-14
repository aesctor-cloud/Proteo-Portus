
variable "vpc_id" {
  description = "ID de la VPC donde se desplegará la instancia"
  type        = string
  
}

variable "sg_ec2_bastion" {
  description = "ID del grupo de seguridad de EC2"
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