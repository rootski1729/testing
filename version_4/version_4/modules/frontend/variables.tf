variable "bucket_name" {
  description = "Name of the S3 bucket for hosting the frontend."
  type        = string
}

variable "domain_name" {
  description = "Fully qualified domain name for the frontend (e.g. acme.hicaliber.net)."
  type        = string
}

variable "acm_certificate_arn" {
  description = "Optional ACM certificate ARN for TLS termination at CloudFront. If not provided, the website is served via HTTP on S3."
  type        = string
  default     = null
}

variable "tags" {
  description = "Tags to apply to frontend resources."
  type        = map(string)
  default     = {}
}