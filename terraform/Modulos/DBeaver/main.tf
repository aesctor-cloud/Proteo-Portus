############################
# 1. Security Group bastión
############################
resource "aws_security_group" "bastion_sg" {
  name        = "${var.instance_name}-sg"
  description = "Bastion for SSM port‑forward to RDS"
  vpc_id      = var.vpc_id

  # Egress únicamente al SG de RDS en 5432
  egress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.rds_sg_id]
  }
}

############################
# 2. AMI Amazon Linux 2023 ARM
############################
data "aws_ami" "al2023_arm" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-minimal-*-arm64"]
  }
}

############################
# 3. Instancia EC2 privada
############################
resource "aws_instance" "bastion" {
  ami                         = data.aws_ami.al2023_arm.id
  instance_type               = "t4g.micro"
  subnet_id                   = var.private_subnet_id
  vpc_security_group_ids      = [aws_security_group.bastion_sg.id]
  iam_instance_profile        = var.iam_profile
  associate_public_ip_address = false  # <- la clave de la privacidad

  tags = {
    Name = var.instance_name
  }
}

############################
# 4. Endpoints SSM
############################
resource "aws_vpc_endpoint" "ssm" {
  for_each = toset([
    "com.amazonaws.eu-west-1.ssm",
    "com.amazonaws.eu-west-1.ssmmessages",
    "com.amazonaws.eu-west-1.ec2messages"
  ])

  vpc_id             = var.vpc_id
  service_name       = each.key
  vpc_endpoint_type  = "Interface"
  subnet_ids         = [var.private_subnet_id]
  security_group_ids = [aws_security_group.bastion_sg.id]

  private_dns_enabled = true
  tags = { Name = "${var.instance_name}-${basename(each.key)}" }
}