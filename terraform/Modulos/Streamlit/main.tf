resource "aws_vpc" "streamlit-vpc" {
  cidr_block       = var.vpc_cidr
  instance_tenancy = "default"
  tags             = merge(var.tags, { Name = "${var.ec2_name}-vpc" })
}
 
resource "aws_internet_gateway" "streamlit-gateway" {
  vpc_id = aws_vpc.streamlit-vpc.id
  tags   = merge(var.tags, { Name = "${var.ec2_name}-igw" })
}
 
resource "aws_subnet" "streamlit-subnet" {
  vpc_id                  = aws_vpc.streamlit-vpc.id
  cidr_block              = var.public_subnet_cidr
  map_public_ip_on_launch = true
  tags                    = merge(var.tags, { Name = "${var.ec2_name}-public-subnet" })
}
 
resource "aws_route_table" "streamlit-route-table" {
  vpc_id = aws_vpc.streamlit-vpc.id
  tags   = merge(var.tags, { Name = "${var.ec2_name}-public-rt" })
}
 
resource "aws_route" "streamlit-route" {
  route_table_id         = aws_route_table.streamlit-route-table.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.streamlit-gateway.id
}
 
resource "aws_route_table_association" "streamlit-association" {
  subnet_id      = aws_subnet.streamlit-subnet.id
  route_table_id = aws_route_table.streamlit-route-table.id
}
 
resource "aws_security_group" "streamlit-security-group" {
  name        = "${var.ec2_name}-sg"
  description = "Security group for Streamlit EC2"
  vpc_id      = aws_vpc.streamlit-vpc.id
  ingress {
    from_port   = var.security_group_ingress_port
    to_port     = var.security_group_ingress_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
 
  tags = merge(var.tags, { Name = "${var.ec2_name}-sg" })
}
 
resource "aws_instance" "streamlit-instance" {
  ami                         = var.ami_id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.streamlit-subnet.id
  iam_instance_profile = var.iam_profile_streamlit
  vpc_security_group_ids      = [aws_security_group.streamlit-security-group.id]
  key_name                    = aws_key_pair.streamlit_key.key_name
  associate_public_ip_address = true
  tags                       = merge(var.tags, { Name = var.ec2_name })
 
  user_data = <<-EOF
    #!/bin/bash
    sudo yum update -y
    sudo yum install -y git python3-pip
    cd /home/ec2-user
    sudo git clone --branch dev https://github.com/aesctor-cloud/Proteo-Portus.git repo
    cd repo/streamlit
    sudo pip3 install --upgrade pip
    sudo pip3 install -r requirements.txt
    streamlit run proteo_portus_app.py 
EOF
}
 
resource "aws_eip" "streamlit-eip" {
  count    = var.assign_elastic_ip ? 1 : 0
  instance = aws_instance.streamlit-instance.id
  domain   = "vpc"
  tags     = merge(var.tags, { Name = "${var.ec2_name}-eip" })
}
 
resource "aws_key_pair" "streamlit_key" {
  key_name   = var.key_name
  public_key = file(var.public_key_path)
}