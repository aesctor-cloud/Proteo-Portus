variable "private_subnets_rds" {
  description = "Private subnets for RDS instance"
  type        = string
}

variable "security_groups_rds" {
  description = "Security groups for RDS instance"
  type        = string
}

variable "db_password" {
  description = "Password for the RDS instance"
  type        = string
}