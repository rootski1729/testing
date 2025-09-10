variable "identifier" {
  description = "Identifier for the PostgreSQL instance."
  type        = string
}

variable "engine_version" {
  description = "PostgreSQL engine version (e.g. 15.4)."
  type        = string
}

variable "instance_class" {
  description = "Instance class for the RDS instance."
  type        = string
}

variable "allocated_storage" {
  description = "Initial allocated storage in GB."
  type        = number
}

variable "username" {
  description = "Master user name for PostgreSQL."
  type        = string
}

variable "password" {
  description = "Master password for PostgreSQL."
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "Name of the PostgreSQL database to create."
  type        = string
}

variable "subnet_ids" {
  description = "List of private subnet IDs for RDS."
  type        = list(string)
}

variable "vpc_id" {
  description = "VPC ID for the RDS security group."
  type        = string
}

variable "backup_retention" {
  description = "Number of days to retain automated backups."
  type        = number
  default     = 7
}

variable "multi_az" {
  description = "Whether to deploy a standby in another AZ for high availability."
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags to apply to all RDS resources."
  type        = map(string)
  default     = {}
}

variable "allowed_security_group_ids" {
  description = "List of security group IDs allowed to access RDS."
  type        = list(string)
  default     = []
}

variable "skip_final_snapshot" {
  description = "Whether to skip final snapshot on database deletion."
  type        = bool
  default     = false
}

variable "deletion_protection" {
  description = "Whether to enable deletion protection for the database."
  type        = bool
  default     = true
}