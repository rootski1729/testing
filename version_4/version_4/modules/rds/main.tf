# Create a subnet group for the RDS instance
resource "aws_db_subnet_group" "this" {
  name       = "${var.identifier}-subnet-group"
  subnet_ids = var.subnet_ids
  tags       = merge(var.tags, { Name = "${var.identifier}-subnet-group" })
}

# Security group for RDS. Allow Postgres (5432) inbound from anywhere within
# the VPC (or refine by referencing compute security group).
resource "aws_security_group" "this" {
  name        = "${var.identifier}-sg"
  description = "Allow Postgres access from ECS services only"
  vpc_id      = var.vpc_id
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = var.allowed_security_group_ids
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = merge(var.tags, { Name = "${var.identifier}-sg" })
}

resource "aws_db_instance" "this" {
  identifier              = var.identifier
  engine                  = "postgres"
  engine_version          = var.engine_version
  instance_class          = var.instance_class
  allocated_storage       = var.allocated_storage
  db_name                 = var.db_name
  username                = var.username
  password                = var.password
  vpc_security_group_ids  = [aws_security_group.this.id]
  db_subnet_group_name    = aws_db_subnet_group.this.name
  multi_az                = var.multi_az
  publicly_accessible     = false
  skip_final_snapshot     = var.skip_final_snapshot
  deletion_protection     = var.deletion_protection
  backup_retention_period = var.backup_retention
  apply_immediately       = true
  storage_encrypted       = true
  auto_minor_version_upgrade = true
  tags = merge(var.tags, { Name = var.identifier })
}

output "endpoint" {
  value = "${aws_db_instance.this.address}:${aws_db_instance.this.port}/${var.db_name}"
}

output "username" {
  value = var.username
}

output "password" {
  value     = var.password
  sensitive = true
}