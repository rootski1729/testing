variable "name" {
  description = "Name prefix for the load balancer."
  type        = string
}

variable "vpc_id" {
  description = "VPC ID in which to deploy the ALB."
  type        = string
}

variable "subnets" {
  description = "List of public subnet IDs for ALB."
  type        = list(string)
}

variable "tags" {
  description = "Tags to apply to all ALB resources."
  type        = map(string)
  default     = {}
}

variable "domain_name" {
  description = "Domain name for ACM certificate (e.g. api-aps.hicaliber.net)"
  type        = string
}

variable "certificate_arn" {
  description = "ARN of ACM certificate for HTTPS. If not provided, will be created."
  type        = string
  default     = null
}

