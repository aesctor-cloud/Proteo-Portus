resource "aws_db_instance" "postgres-db-instance" {
  allocated_storage    = 20
  db_name = "postgresdb"
  db_subnet_group_name = var.private_subnets_rds
  engine               = "postgres"
  engine_version       = "16.3"
  identifier           = "postgres-db"
  instance_class       = "db.t3.micro"
  password             = var.db_password
  skip_final_snapshot  = true
  storage_encrypted    = false
  publicly_accessible   = false
  username             = "postgres"
  apply_immediately    = true
  multi_az = false  #* Menor disponibilidad, más tolerancia a fallos, pero más económico
  vpc_security_group_ids = [var.security_groups_rds]
  tags = {
    Name = "postgres-db-instance"
  }
}
