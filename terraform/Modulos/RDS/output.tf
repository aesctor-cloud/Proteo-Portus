output "db_host" {
  description = "The host of the RDS instance"
  value       = aws_db_instance.postgres-db-instance.address
  
}

output "db_port" {
  description = "The port of the RDS instance"
  value       = aws_db_instance.postgres-db-instance.port
}

output "db_name" {
  description = "The name of the RDS instance"
  value       = aws_db_instance.postgres-db-instance.db_name
}

output "db_user" {
  description = "The user of the RDS instance"
  value       = aws_db_instance.postgres-db-instance.username
}

output "db_password" {
  description = "The password of the RDS instance"
  value       = aws_db_instance.postgres-db-instance.password
}