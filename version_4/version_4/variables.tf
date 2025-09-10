variable "client_name" {
  description = "Single-word CamelCase name of the client (e.g. APSInsurance, Acme, AcmeCorp). Use 'SaaSShared' when provisioning shared SaaS infrastructure."
  type        = string
}

variable "plan" {
  description = "Deployment plan: 'SaaS' for shared multi‑tenant deployments or 'Dedicated' for isolated per‑client stacks."
  type        = string
  validation {
    condition     = contains(["SaaS", "Dedicated"], var.plan)
    error_message = "plan must be either 'SaaS' or 'Dedicated'"
  }
}

variable "env" {
  description = "Environment name (e.g. stg or prod)."
  type        = string
  validation {
    condition     = contains(["stg", "prod"], var.env)
    error_message = "env must be 'stg' or 'prod'"
  }
}

variable "subdomain" {
  description = "Subdomain for the client (e.g. acme for acme.hicaliber.net). For SaaS this could be 'saas-customer' or 'demo'."
  type        = string
}

variable "aws_region" {
  description = "AWS region to deploy into."
  type        = string
  default     = "ap-south-1"
}

variable "tags" {
  description = "Global tags applied to every resource."
  type        = map(string)
  default     = {}
}

variable "saas_documentdb_uri" {
  description = "For SaaS tenants, provide the connection string URI of the shared Amazon DocumentDB cluster (including required parameters)."
  type        = string
  default     = null
}

variable "saas_rds_endpoint" {
  description = "For SaaS tenants, provide the endpoint of the shared PostgreSQL RDS instance in the format host:port/dbname."
  type        = string
  default     = null
}

variable "saas_api_lb_dns_name" {
  description = "For SaaS tenants, provide the DNS name of the shared API load balancer."
  type        = string
  default     = null
}

variable "saas_api_lb_zone_id" {
  description = "For SaaS tenants, provide the Route53 zone ID of the shared API load balancer."
  type        = string
  default     = null
}

variable "acm_certificate_arn" {
  description = "ARN of an ACM certificate for the domain, if TLS termination at the ALB or CloudFront is desired."
  type        = string
  default     = null
}

# The following variables allow customization of compute resources. Defaults are
# intentionally conservative to minimize cost. Adjust as needed.
variable "api_container_image" {
  description = "Docker image for the Django API container. Must use ECR format with digest pinning: <account>.dkr.ecr.<region>.amazonaws.com/<repo>@sha256:<digest>"
  type        = string
  default     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/caliber-api@sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"  # Replace with actual ECR image digest
  validation {
    condition     = can(regex("^[0-9]+\\.dkr\\.ecr\\.[a-z0-9-]+\\.amazonaws\\.com\\/[a-z0-9-]+@sha256:[a-f0-9]{64}$", var.api_container_image))
    error_message = "api_container_image must be in ECR format with SHA256 digest: <account>.dkr.ecr.<region>.amazonaws.com/<repo>@sha256:<digest>"
  }
}

variable "frontend_bucket_name" {
  description = "Optional override for the S3 bucket used to host the React frontend. If not specified it will be derived from the client and environment."
  type        = string
  default     = null
}