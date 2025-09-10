variable "cluster_identifier" {
  description = "Unique name for the DocumentDB cluster."
  type        = string
}

variable "instance_class" {
  description = "Instance class for DocumentDB instances (e.g. db.r6g.large)."
  type        = string
}

variable "instance_count" {
  description = "Number of DocumentDB instances to create."
  type        = number
  default     = 1
}

variable "username" {
  description = "Master username for DocumentDB."
  type        = string
}

variable "password" {
  description = "Master password for DocumentDB."
  type        = string
  sensitive   = true
}

variable "subnet_ids" {
  description = "List of private subnet IDs for DocumentDB."
  type        = list(string)
}

variable "vpc_id" {
  description = "VPC ID to attach the DocumentDB security group."
  type        = string
}

variable "tags" {
  description = "Tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "allowed_security_group_ids" {
  description = "List of security group IDs allowed to access DocumentDB."
  type        = list(string)
  default     = []
}

variable "skip_final_snapshot" {
  description = "Whether to skip final snapshot on cluster deletion."
  type        = bool
  default     = false
}

variable "deletion_protection" {
  description = "Whether to enable deletion protection for the cluster."
  type        = bool
  default     = true
}

variable "backup_retention_period" {
  description = "Number of days to retain automated backups."
  type        = number
  default     = 7
}