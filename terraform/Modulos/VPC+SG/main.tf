# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true  
  enable_dns_support   = true  
  
  tags = {
    Name = "vpc-rds"
  }
}

# Subnets privadas
resource "aws_subnet" "private_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "eu-west-1a" 
  map_public_ip_on_launch = false        
  tags = {
    Name = "private-subnet_a"
  }
}

resource "aws_subnet" "private_b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "eu-west-1b" 
  map_public_ip_on_launch = false        
  tags = {
    Name = "private-subnet_b"
  }
}

# DB Subnet Group
resource "aws_db_subnet_group" "rds_subnet_group" {
  name       = "rds-subnet-group"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]
  tags = {
    Name = "rds-subnet-group"
  }
}

# Security Group para Lambda - SIN REFERENCIAS A OTROS SG
resource "aws_security_group" "lambda_sg" {
  name        = "lambda_sg"
  description = "Security group for Lambda functions"
  vpc_id      = aws_vpc.main.id

  # Salida completa para simplificar (puedes restringir después)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name = "lambda-security-group"
  }
}

# REGLAS SEPARADAS PARA EVITAR DEPENDENCIAS CIRCULARES
resource "aws_security_group_rule" "rds_allow_lambda" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.lambda_sg.id
  security_group_id        = aws_security_group.rds_sg.id
  description              = "PostgreSQL from Lambda"

}

resource "aws_security_group_rule" "rds_allow_bastion" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.bastion_sg.id
  security_group_id        = aws_security_group.rds_sg.id
  description              = "PostgreSQL from Bastion"
}

# Security Group para RDS - SIN REFERENCIAS EN LÍNEA
resource "aws_security_group" "rds_sg" {
  name        = "rds_sg"
  description = "Allow access to RDS"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "rds-security-group"
  }
}

# Security Group para VPC Endpoints - SIN REFERENCIAS A OTROS SG
resource "aws_security_group" "vpc_endpoint" {
  name        = "vpce-sg"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.lambda_sg.id]
    description     = "Allow Lambda to use VPC Endpoint"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "vpc-endpoint-security-group"
  }
}

# Security Group para SSM VPC Endpoint
# Security Group para Bastion
resource "aws_security_group" "bastion_sg" {
  name        = "Proteo-Instance-Dbeaver-sg-v2"
  description = "Bastion for SSM portforward to RDS"
  vpc_id      = aws_vpc.main.id
}

# Egress a RDS
resource "aws_security_group_rule" "bastion_to_rds" {
  type                     = "egress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = aws_security_group.bastion_sg.id
  source_security_group_id = aws_security_group.rds_sg.id
  description              = "Allow traffic to RDS"
}

# Egress a SSM VPC Endpoints
resource "aws_security_group_rule" "bastion_to_ssm" {
  type                     = "egress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.bastion_sg.id
  source_security_group_id = aws_security_group.ssm_vpce_sg.id
  description              = "Allow traffic to SSM Endpoints"
}

# Security Group para SSM Endpoints
resource "aws_security_group" "ssm_vpce_sg" {
  name   = "ssm-vpce-sg"
  vpc_id = aws_vpc.main.id
}

resource "aws_security_group_rule" "ssm_allow_bastion" {
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.ssm_vpce_sg.id
  source_security_group_id = aws_security_group.bastion_sg.id
  description              = "Allow Bastion EC2 to connect to SSM endpoint"
}


# VPC Endpoint para CloudWatch Logs
resource "aws_vpc_endpoint" "logs" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.eu-west-1.logs"
  vpc_endpoint_type = "Interface"
  subnet_ids        = [aws_subnet.private_a.id, aws_subnet.private_b.id]
  security_group_ids = [aws_security_group.vpc_endpoint.id]
  tags = {
    Name = "vpc-endpoint-logs"
  }
}

# VPC Endpoint para Bedrock Agent
resource "aws_vpc_endpoint" "BedrockAgent" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.eu-west-1.bedrock-runtime"
  vpc_endpoint_type = "Interface"
  subnet_ids        = [aws_subnet.private_a.id, aws_subnet.private_b.id]
  security_group_ids = [aws_security_group.vpc_endpoint.id]
  private_dns_enabled = true
  tags = {
    Name = "vpc-endpoint-bedrock-agent"
  }
}

# Endpoints SSM
resource "aws_vpc_endpoint" "ssm_endpoint" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.eu-west-1.ssm"
  vpc_endpoint_type = "Interface"
  subnet_ids        = [aws_subnet.private_a.id, aws_subnet.private_b.id]
  security_group_ids = [aws_security_group.ssm_vpce_sg.id]
  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "ssmmessages_endpoint" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.eu-west-1.ssmmessages"
  vpc_endpoint_type = "Interface"
  subnet_ids        = [aws_subnet.private_a.id, aws_subnet.private_b.id]
  security_group_ids = [aws_security_group.ssm_vpce_sg.id]
  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "ec2messages_endpoint" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.eu-west-1.ec2messages"
  vpc_endpoint_type = "Interface"
   subnet_ids        = [aws_subnet.private_a.id, aws_subnet.private_b.id]
  security_group_ids = [aws_security_group.ssm_vpce_sg.id]
  private_dns_enabled = true
}

# VPC Endpoint para S3
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "private-route-table"
  }
}

resource "aws_route_table_association" "private_a_assoc" {
  subnet_id      = aws_subnet.private_a.id
  route_table_id = aws_route_table.private.id

}

resource "aws_route_table_association" "private_b_assoc" {
  subnet_id      = aws_subnet.private_b.id
  route_table_id = aws_route_table.private.id
}

resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.eu-west-1.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private.id]
  tags = {
    Name = "vpc-endpoint-s3"
  }
}
