output "security_groups_rds" {
  value = aws_security_group.rds_sg.id
}

output "private_subnets_rds" {
  value = aws_db_subnet_group.rds_subnet_group.name
}

output "subnet_a_id" {
  value = aws_subnet.private_a.id
}

output "subnet_b_id" {
  value = aws_subnet.private_b.id
}

output "security_group_lambda" {
  value = aws_security_group.lambda_sg.id
}

output "vpc_id" {
  value = aws_vpc.main.id
}

output "sg_ec2_bastion" {
  value = aws_security_group.bastion_sg.id
}