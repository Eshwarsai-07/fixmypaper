resource "aws_db_instance" "main" {
  allocated_storage      = 20
  db_name                = var.db_name
  engine                 = "postgres"
  engine_version         = "15"
  instance_class         = "db.t3.micro"
  username               = var.db_user
  password               = var.db_password
  parameter_group_name   = "default.postgres15"
  vpc_security_group_ids = [var.vpc_sg_id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  skip_final_snapshot    = true

  tags = {
    Name = "${var.project_name}-rds"
  }
}

resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = var.subnet_ids

  tags = {
    Name = "${var.project_name}-db-subnet-group"
  }
}
