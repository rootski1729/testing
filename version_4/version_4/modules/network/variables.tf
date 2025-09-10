variable "create_vpc" {
  description = "Whether to create a new VPC or reuse an existing one."
  type        = bool
}

variable "vpc_name" {
  description = "Name prefix for the VPC."
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
}

variable "az_count" {
  description = "Number of availability zones to spread subnets across."
  type        = number
  default     = 2
}

variable "public_subnet_cidrs" {
  description = "List of CIDR blocks for public subnets. Must match az_count in length."
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "List of CIDR blocks for private subnets. Must match az_count in length."
  type        = list(string)
}

variable "single_nat_gateway" {
  description = "If true, create a single NAT gateway in the first public subnet to reduce cost. Otherwise one per AZ."
  type        = bool
  default     = true
}

variable "enable_endpoints" {
  description = "Whether to create VPC endpoints for S3, ECR, CloudWatch Logs and Secrets Manager."
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags to apply to resources."
  type        = map(string)
  default     = {}
}