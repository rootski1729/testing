# Security group for the ALB
resource "aws_security_group" "this" {
  name        = "${var.name}-alb-sg"
  description = "Allow HTTP/HTTPS access to the ALB"
  vpc_id      = var.vpc_id
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  # Egress rules will be added separately to avoid circular dependency
  tags = merge(var.tags, { Name = "${var.name}-alb-sg" })
}

# Application Load Balancer
resource "aws_lb" "this" {
  name               = var.name
  load_balancer_type = "application"
  internal           = false
  security_groups    = [aws_security_group.this.id]
  subnets            = var.subnets
  idle_timeout       = 60
  enable_deletion_protection = false
  tags               = var.tags
}

# Target group for ECS tasks. Target group listens on port 80 and forwards
# requests to the ECS container port (defined in the compute module). Health
# checks are configured to query the /healthz endpoint on port 8000.
resource "aws_lb_target_group" "this" {
  name        = "${var.name}-tg"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"
  health_check {
    enabled             = true
    path                = "/healthz"
    port                = "traffic-port"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    interval            = 30
    timeout             = 5
    matcher             = "200"
  }
  tags = var.tags
}

# Data source to find Route53 hosted zone
data "aws_route53_zone" "main" {
  name         = join(".", slice(split(".", var.domain_name), 1, length(split(".", var.domain_name))))
  private_zone = false
}

# Create ACM certificate if not provided
resource "aws_acm_certificate" "this" {
  count             = var.certificate_arn == null ? 1 : 0
  domain_name       = var.domain_name
  validation_method = "DNS"
  
  lifecycle {
    create_before_destroy = true
  }
  
  tags = var.tags
}

# DNS validation records for ACM
resource "aws_route53_record" "cert_validation" {
  for_each = var.certificate_arn == null ? {
    for dvo in aws_acm_certificate.this[0].domain_validation_options : dvo.domain_name => {
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

# ACM certificate validation
resource "aws_acm_certificate_validation" "this" {
  count                   = var.certificate_arn == null ? 1 : 0
  certificate_arn         = aws_acm_certificate.this[0].arn
  validation_record_fqdns = [for r in aws_route53_record.cert_validation : r.fqdn]
}

locals {
  certificate_arn = var.certificate_arn != null ? var.certificate_arn : aws_acm_certificate.this[0].arn
}

# HTTPS Listener (443)
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.this.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = local.certificate_arn
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.this.arn
  }
  
  depends_on = [aws_acm_certificate_validation.this]
}

# HTTP Listener (80) - Redirect to HTTPS
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.this.arn
  port              = 80
  protocol          = "HTTP"
  
  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

output "lb_dns_name" {
  value = aws_lb.this.dns_name
}

output "lb_zone_id" {
  value = aws_lb.this.zone_id
}

output "target_group_arn" {
  value = aws_lb_target_group.this.arn
}

output "security_group_id" {
  description = "Security group ID for the ALB"
  value       = aws_security_group.this.id
}