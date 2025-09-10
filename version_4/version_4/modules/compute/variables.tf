variable "cluster_name" {
  description = "Name of the ECS cluster."
  type        = string
}

variable "vpc_id" {
  description = "VPC ID for ECS networking."
  type        = string
}

variable "vpc_cidr" {
  description = "VPC CIDR block for DNS resolver access."
  type        = string
}

variable "subnets" {
  description = "List of private subnet IDs for ECS tasks."
  type        = list(string)
}

variable "alb_target_group" {
  description = "ARN of the ALB target group to register the ECS service."
  type        = string
}

variable "image" {
  description = "Docker image to run for the API."
  type        = string
}

variable "container_port" {
  description = "Port on which the application listens inside the container."
  type        = number
  default     = 8000
}

variable "desired_count" {
  description = "Number of desired ECS tasks."
  type        = number
  default     = 1
}

variable "documentdb_uri" {
  description = "Connection URI for DocumentDB to inject into the container environment."
  type        = string
}

variable "rds_endpoint" {
  description = "PostgreSQL endpoint with port and database name (host:port/dbname)."
  type        = string
}

variable "secrets_prefix" {
  description = "Prefix used when storing secrets in Secrets Manager. Unused here but reserved for future use."
  type        = string
}

variable "tags" {
  description = "Tags to apply to ECS resources."
  type        = map(string)
  default     = {}
}

variable "alb_security_group_id" {
  description = "Security group ID of the ALB to allow inbound traffic from."
  type        = string
}

variable "docdb_secret_arn" {
  description = "ARN of the DocumentDB credentials secret in Secrets Manager."
  type        = string
  default     = ""
}

variable "rds_secret_arn" {
  description = "ARN of the RDS credentials secret in Secrets Manager."
  type        = string
  default     = ""
}