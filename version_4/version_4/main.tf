# Fetch the hosted zone for hicaliber.net. You must own this domain in Route 53.
data "aws_route53_zone" "primary" {
  name         = "hicaliber.net."
  private_zone = false
}

###############################################################################
# Networking
# A VPC is created for each Dedicated deployment. For SaaS, a single VPC is
# created when provisioning the "SaaSShared" client. Subsequent SaaS tenants
# reuse the shared VPC via data lookups. This simplifies sharing compute and
# database resources while still allowing per‑tenant DNS configuration.
###############################################################################

# Determine whether to create a new VPC. We create a VPC only when either the
# plan is Dedicated or the client is SaaSShared. SaaS tenants reuse the shared
# VPC from the SaaSShared state. If you have previously run `terraform apply`
# with client_name="SaaSShared" then the shared VPC will already exist.
locals {
  create_new_vpc = var.plan == "Dedicated" || var.client_name == "SaaSShared"
}

module "network" {
  source = "./modules/network"

  # Only create the networking resources when required. When not creating, the
  # module still outputs values by reading from data sources.
  create_vpc     = local.create_new_vpc
  vpc_name       = local.name_prefix
  vpc_cidr       = "10.${random_integer.cidr.result}.0.0/16"
  az_count       = 2
  public_subnet_cidrs  = ["10.${random_integer.cidr.result}.0.0/24", "10.${random_integer.cidr.result}.1.0/24"]
  private_subnet_cidrs = ["10.${random_integer.cidr.result}.100.0/24", "10.${random_integer.cidr.result}.101.0/24"]
  single_nat_gateway   = true
  enable_endpoints     = true
  tags                 = local.base_tags

  providers = {
    aws = aws
  }
}

# Random integer used to avoid CIDR collisions when multiple stacks are deployed
# in the same account. Because Terraform cannot compute random numbers at
# apply time, this resource persists the value in the state file. Removing
# random_integer or changing its parameters will recreate the VPC.
resource "random_integer" "cidr" {
  min = 1
  max = 250
}

###############################################################################
# Databases
# Only provision databases when either Dedicated plan is selected or when
# provisioning the SaaSShared client. Additional SaaS tenants will reuse
# existing DocumentDB and RDS instances (exported via remote state).
###############################################################################

locals {
  create_docdb = var.plan == "Dedicated" || var.client_name == "SaaSShared"
  create_rds   = var.plan == "Dedicated" || var.client_name == "SaaSShared"
}

module "docdb" {
  source  = "./modules/documentdb"
  count   = local.create_docdb ? 1 : 0

  cluster_identifier      = "${local.name_prefix}-docdb"
  instance_class          = "db.t4g.medium"  # DocumentDB minimum supported instance
  instance_count          = 1
  username                = "admin"
  password                = random_password.docdb.result
  subnet_ids              = module.network.private_subnet_ids
  vpc_id                  = module.network.vpc_id
  allowed_security_group_ids = local.create_compute ? [module.compute[0].security_group_id] : []
  skip_final_snapshot     = !local.is_prod  # Take snapshots in prod
  deletion_protection     = local.is_prod   # Protect prod databases
  backup_retention_period = local.is_prod ? 30 : 7
  tags                    = local.base_tags

  providers = {
    aws = aws
  }
}

# DocumentDB credentials in Secrets Manager
resource "aws_secretsmanager_secret" "docdb" {
  name                    = "${local.client_lower}-${var.env}-docdb-credentials"
  description             = "DocumentDB credentials for ${var.client_name}-${var.env}"
  recovery_window_in_days = local.is_prod ? 30 : 0
  tags                    = local.base_tags
}

resource "aws_secretsmanager_secret_version" "docdb" {
  secret_id = aws_secretsmanager_secret.docdb.id
  secret_string = jsonencode({
    username = "admin"
    password = random_password.docdb.result
  })
}

resource "random_password" "docdb" {
  length  = 20
  special = true
}

module "rds" {
  source  = "./modules/rds"
  count   = local.create_rds ? 1 : 0

  identifier           = "${local.name_prefix}-postgres"
  engine_version       = "15.4"
  instance_class       = "db.t4g.small"  # Cost optimization: smallest instance type
  allocated_storage    = 20
  username             = "admin"
  password             = random_password.rds.result
  db_name              = "caliber_${local.client_lower}"
  subnet_ids           = module.network.private_subnet_ids
  vpc_id               = module.network.vpc_id
  allowed_security_group_ids = local.create_compute ? [module.compute[0].security_group_id] : []
  skip_final_snapshot  = !local.is_prod  # Take snapshots in prod
  deletion_protection  = local.is_prod   # Protect prod databases
  tags                 = local.base_tags
  backup_retention     = local.is_prod ? 30 : 7
  multi_az             = false  # Cost optimization: single AZ deployment

  providers = {
    aws = aws
  }
}

# RDS credentials in Secrets Manager
resource "aws_secretsmanager_secret" "rds" {
  name                    = "${local.client_lower}-${var.env}-rds-credentials"
  description             = "RDS PostgreSQL credentials for ${var.client_name}-${var.env}"
  recovery_window_in_days = local.is_prod ? 30 : 0
  tags                    = local.base_tags
}

resource "aws_secretsmanager_secret_version" "rds" {
  secret_id = aws_secretsmanager_secret.rds.id
  secret_string = jsonencode({
    username = "admin"
    password = random_password.rds.result
  })
}

resource "random_password" "rds" {
  length  = 20
  special = true
}

# Random suffix to ensure bucket names are globally unique
resource "random_string" "bucket_suffix" {
  length  = 8
  upper   = false
  special = false
}

###############################################################################
# Compute (API) and Load Balancer
# Provision compute resources only for dedicated stacks or for the shared SaaS
# infrastructure. SaaS tenants reuse these resources via DNS.
###############################################################################

locals {
  create_compute = var.plan == "Dedicated" || var.client_name == "SaaSShared"
}

module "alb" {
  source  = "./modules/alb"
  count   = local.create_compute ? 1 : 0
  name           = "${local.name_prefix}-api"
  vpc_id         = module.network.vpc_id
  subnets        = module.network.public_subnet_ids
  domain_name    = local.api_fqdn
  certificate_arn = var.acm_certificate_arn
  tags           = local.base_tags

  providers = {
    aws = aws
  }
}

module "compute" {
  source  = "./modules/compute"
  count   = local.create_compute ? 1 : 0

  cluster_name       = "${local.name_prefix}-cluster"
  vpc_id             = module.network.vpc_id
  vpc_cidr           = module.network.vpc_cidr
  subnets            = module.network.private_subnet_ids
  # Only reference the ALB target group when compute resources are being created.  When
  # this is a SaaS tenant relying on shared compute the variable can be an empty
  # string; the compute module itself will be skipped via its count.
  alb_target_group   = local.create_compute ? module.alb[0].target_group_arn : ""
  alb_security_group_id = local.create_compute ? module.alb[0].security_group_id : ""
  image              = var.api_container_image
  container_port     = 8000
  desired_count      = 1  # Cost optimization: single task deployment
  documentdb_uri     = local.create_docdb ? module.docdb[0].connection_uri : var.saas_documentdb_uri
  rds_endpoint       = local.create_rds ? module.rds[0].endpoint : var.saas_rds_endpoint
  docdb_secret_arn   = local.create_docdb ? aws_secretsmanager_secret.docdb.arn : ""
  rds_secret_arn     = local.create_rds ? aws_secretsmanager_secret.rds.arn : ""
  secrets_prefix     = "${local.client_lower}-${var.env}"
  tags               = local.base_tags

  providers = {
    aws = aws
  }
}

# ALB security group egress rule to ECS tasks (created after both modules)
resource "aws_security_group_rule" "alb_to_ecs" {
  count                    = local.create_compute ? 1 : 0
  type                     = "egress"
  from_port                = 8000
  to_port                  = 8000
  protocol                 = "tcp"
  security_group_id        = module.alb[0].security_group_id
  source_security_group_id = module.compute[0].security_group_id
  description              = "Allow ALB to communicate with ECS tasks on container port"
}

###############################################################################
# Frontend hosting
# Always provision a bucket/CloudFront distribution per client. Even SaaS
# tenants get their own bucket and distribution so that React builds can be
# customized per customer. If you prefer a shared frontend, set
# var.frontend_bucket_name for SaaS clients.
###############################################################################

module "frontend" {
  source = "./modules/frontend"
  bucket_name = var.frontend_bucket_name != null ? var.frontend_bucket_name : "${local.name_prefix}-frontend-${random_string.bucket_suffix.result}"
  # Set the domain name for the frontend to a separate FQDN.  See locals
  # definition for details.  This ensures the API and frontend records do not
  # collide in Route 53.
  domain_name = local.frontend_fqdn
  acm_certificate_arn = var.acm_certificate_arn
  tags = local.base_tags

  providers = {
    aws           = aws
    aws.us_east_1 = aws.us_east_1
  }
}

###############################################################################
# DNS records
# Create an A record for the API and a CNAME or A record for the frontend. For
# dedicated and shared SaaS stacks the API record points directly at the ALB.
# SaaS tenants (client != SaaSShared) point their API record at the shared
# infrastructure's ALB. The frontend record always points at the CloudFront
# distribution if used, otherwise to the S3 website endpoint.
###############################################################################

resource "aws_route53_record" "api" {
  zone_id = data.aws_route53_zone.primary.zone_id
  name    = local.api_fqdn
  type    = "A"

  # Use alias when ALB is provisioned by this stack. Otherwise require the
  # caller to provide the shared ALB DNS name via variable. The alias ensures
  # the host header is preserved end to end.
  alias {
    name                   = local.create_compute ? module.alb[0].lb_dns_name : var.saas_api_lb_dns_name
    zone_id                = local.create_compute ? module.alb[0].lb_zone_id    : var.saas_api_lb_zone_id
    evaluate_target_health = true
  }

  depends_on = [module.alb]
}

# Record for the static website / CloudFront
resource "aws_route53_record" "frontend" {
  zone_id = data.aws_route53_zone.primary.zone_id
  # Publish the frontend under the www. prefix subdomain.  We cannot have
  # multiple record types on the same name so the API and frontend use
  # separate hosts.
  name    = local.frontend_fqdn
  type    = "CNAME"
  ttl     = 300
  records = [module.frontend.domain_name]
}