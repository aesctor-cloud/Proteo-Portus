output "ec2_public_ip" {
  description = "IP pública de la instancia EC2 (Elastic IP si está asignada)"
  value       = var.assign_elastic_ip ? aws_eip.streamlit-eip[0].public_ip : aws_instance.streamlit-instance.public_ip
}
 
output "ec2_public_dns" {
  description = "DNS público de la instancia EC2"
  value       = aws_instance.streamlit-instance.public_dns
}
 
output "ec2_id" {
  description = "ID de la instancia EC2"
  value       = aws_instance.streamlit-instance.id
}