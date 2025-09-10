# S3 bucket for static site (private)
resource "aws_s3_bucket" "this" {
  bucket        = var.bucket_name
  force_destroy = true
  tags          = var.tags
}

# Block all public access to S3 bucket
resource "aws_s3_bucket_public_access_block" "this" {
  bucket = aws_s3_bucket.this.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CloudFront Origin Access Control (OAC) - replaces deprecated OAI
resource "aws_cloudfront_origin_access_control" "this" {
  name                              = "${var.bucket_name}-oac"
  description                       = "OAC for ${var.bucket_name}"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# Create ACM certificate for frontend if not provided
data "aws_route53_zone" "main" {
  name         = join(".", slice(split(".", var.domain_name), 1, length(split(".", var.domain_name))))
  private_zone = false
}

resource "aws_acm_certificate" "frontend" {
  count             = var.acm_certificate_arn == null ? 1 : 0
  domain_name       = var.domain_name
  validation_method = "DNS"
  
  # CloudFront requires certificates in us-east-1
  provider = aws.us_east_1
  
  lifecycle {
    create_before_destroy = true
  }
  
  tags = var.tags
}

# DNS validation records for frontend ACM certificate
resource "aws_route53_record" "frontend_cert_validation" {
  for_each = var.acm_certificate_arn == null ? {
    for dvo in aws_acm_certificate.frontend[0].domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      type   = dvo.resource_record_type
      record = dvo.resource_record_value
    }
  } : {}
  
  name    = each.value.name
  type    = each.value.type
  zone_id = data.aws_route53_zone.main.zone_id
  records = [each.value.record]
  ttl     = 300
}

# Frontend ACM certificate validation
resource "aws_acm_certificate_validation" "frontend" {
  count                   = var.acm_certificate_arn == null ? 1 : 0
  certificate_arn         = aws_acm_certificate.frontend[0].arn
  validation_record_fqdns = [for r in aws_route53_record.frontend_cert_validation : r.fqdn]
  
  provider = aws.us_east_1
}

locals {
  frontend_certificate_arn = var.acm_certificate_arn != null ? var.acm_certificate_arn : aws_acm_certificate.frontend[0].arn
}

# CloudFront distribution
resource "aws_cloudfront_distribution" "this" {
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  aliases             = [var.domain_name]
  
  origin {
    domain_name              = aws_s3_bucket.this.bucket_regional_domain_name
    origin_id                = "S3-${aws_s3_bucket.this.id}"
    origin_access_control_id = aws_cloudfront_origin_access_control.this.id
  }
  
  default_cache_behavior {
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-${aws_s3_bucket.this.id}"
    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    
    cache_policy_id = "658327ea-f89d-4fab-a63d-7e88639e58f6"  # Managed-CachingOptimized
  }
  
  # Custom error pages for SPA (return index.html for 404s)
  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }
  
  custom_error_response {
    error_code         = 403
    response_code      = 200
    response_page_path = "/index.html"
  }
  
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  
  viewer_certificate {
    acm_certificate_arn      = local.frontend_certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }
  
  depends_on = [aws_acm_certificate_validation.frontend]
  tags       = var.tags
}

# S3 bucket policy to allow CloudFront OAC access
resource "aws_s3_bucket_policy" "this" {
  bucket = aws_s3_bucket.this.id
  policy = data.aws_iam_policy_document.s3_policy.json
}

data "aws_iam_policy_document" "s3_policy" {
  statement {
    sid    = "AllowCloudFrontServicePrincipal"
    effect = "Allow"
    
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }
    
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.this.arn}/*"]
    
    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.this.arn]
    }
  }
}

# Output the CloudFront domain
output "domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = aws_cloudfront_distribution.this.domain_name
}

output "distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.this.id
}

output "s3_bucket" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.this.id
}