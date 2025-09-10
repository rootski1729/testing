output "api_endpoint" {
  description = "Public DNS name of the API load balancer.  For SaaS tenants this will return the provided shared load balancer." 
  value       = try(module.alb[0].lb_dns_name, var.saas_api_lb_dns_name)
}

output "documentdb_uri" {
  description = "Connection string for Amazon DocumentDB. Includes required parameters for TLS, replica set, and disabled retryable writes."
  value       = try(module.docdb[0].connection_uri, var.saas_documentdb_uri)
  sensitive   = true
}

output "postgresql_endpoint" {
  description = "Endpoint and port for the PostgreSQL instance."
  value       = try(module.rds[0].endpoint, var.saas_rds_endpoint)
  sensitive   = true
}

output "frontend_url" {
  description = "URL of the deployed React frontend (either CloudFront distribution or direct S3 static site)."
  value       = module.frontend.domain_name
}

output "frontend_distribution_id" {
  description = "CloudFront distribution ID for the frontend, if CloudFront is used. Empty when using S3 website hosting."
  value       = module.frontend.distribution_id
}

output "hosted_zone_id" {
  description = "Route53 hosted zone ID used for DNS record creation."
  value       = data.aws_route53_zone.primary.zone_id
}