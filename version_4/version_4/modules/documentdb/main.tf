# Create a subnet group for DocumentDB
resource "aws_docdb_subnet_group" "this" {
  name       = "${var.cluster_identifier}-subnet-group"
  subnet_ids = var.subnet_ids
  tags       = merge(var.tags, { Name = "${var.cluster_identifier}-subnet-group" })
}

# DocumentDB cluster parameter group to enforce TLS
resource "aws_docdb_cluster_parameter_group" "this" {
  family = "docdb5.0"
  name   = "${var.cluster_identifier}-params"
  
  parameter {
    name  = "tls"
    value = "enabled"
  }
  
  tags = merge(var.tags, { Name = "${var.cluster_identifier}-params" })
}

# Security group for DocumentDB allowing inbound traffic on port 27017 from the
# VPC CIDR. In production you should restrict this to only the ECS tasks
# security group.
resource "aws_security_group" "this" {
  name        = "${var.cluster_identifier}-sg"
  description = "Allow DocumentDB access from ECS services only"
  vpc_id      = var.vpc_id
  ingress {
    from_port       = 27017
    to_port         = 27017
    protocol        = "tcp"
    security_groups = var.allowed_security_group_ids
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = merge(var.tags, { Name = "${var.cluster_identifier}-sg" })
}

resource "aws_docdb_cluster" "this" {
  cluster_identifier      = var.cluster_identifier
  engine                  = "docdb"
  master_username         = var.username
  master_password         = var.password
  skip_final_snapshot     = var.skip_final_snapshot
  deletion_protection     = var.deletion_protection
  apply_immediately           = true
  db_subnet_group_name        = aws_docdb_subnet_group.this.name
  db_cluster_parameter_group_name = aws_docdb_cluster_parameter_group.this.name
  vpc_security_group_ids      = [aws_security_group.this.id]
  backup_retention_period = var.backup_retention_period
  preferred_backup_window = "02:00-03:00"
  storage_encrypted       = true
  enabled_cloudwatch_logs_exports = ["audit", "profiler"]
  tags = merge(var.tags, { Name = var.cluster_identifier })
}

resource "aws_docdb_cluster_instance" "this" {
  count               = var.instance_count
  identifier          = "${var.cluster_identifier}-${count.index}"
  cluster_identifier  = aws_docdb_cluster.this.id
  instance_class      = var.instance_class
  apply_immediately   = true
  tags                = merge(var.tags, { Name = "${var.cluster_identifier}-instance-${count.index}" })
}

# Construct a MongoDB‑compatible connection URI. Amazon DocumentDB requires
# TLS/SSL, specifies the replica set name "rs0", and disables retryable writes.
locals {
  endpoint    = aws_docdb_cluster.this.endpoint
  port        = aws_docdb_cluster.this.port
  username    = var.username
  password    = var.password
  connection_uri = "mongodb://${var.username}:${var.password}@${aws_docdb_cluster.this.endpoint}:${aws_docdb_cluster.this.port}/?ssl=true&replicaSet=rs0&retryWrites=false"
}

output "endpoint" {
  value = local.endpoint
}

output "port" {
  value = local.port
}

output "username" {
  value = local.username
}

output "password" {
  value     = local.password
  sensitive = true
}

output "connection_uri" {
  value     = local.connection_uri
  sensitive = true
}