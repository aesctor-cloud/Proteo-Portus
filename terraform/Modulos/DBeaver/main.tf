############################
# 2. AMI Amazon Linux 2023 ARM
############################
data "aws_ami" "al2023_x86" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

############################
# 3. Instancia EC2 privada
############################
resource "aws_instance" "bastion" {
  ami                         = data.aws_ami.al2023_x86.id
  instance_type               = "t3.micro"
  subnet_id                   = var.private_subnet_id
  vpc_security_group_ids      = [var.sg_ec2_bastion]
  iam_instance_profile        = var.iam_profile
  associate_public_ip_address = false  # <- la clave de la privacidad

  tags = {
    Name = "Proteo-Instance-Dbeaver"
  }
}

