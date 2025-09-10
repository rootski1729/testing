locals {
  azs          = slice(data.aws_availability_zones.available.names, 0, var.az_count)
  use_existing = !var.create_vpc
}

data "aws_availability_zones" "available" {}

# Either create a new VPC or look up an existing one by tags. The naming
# convention for shared VPCs relies on the Client=SaaSShared tag and matching
# environment.
resource "aws_vpc" "this" {
  count = var.create_vpc ? 1 : 0
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = merge(var.tags, {
    Name = var.vpc_name
  })
}

data "aws_vpc" "shared" {
  count = var.create_vpc ? 0 : 1
  filter {
    name   = "tag:Client"
    values = [var.tags["Client"]]
  }
  filter {
    name   = "tag:Plan"
    values = ["SaaS"]
  }
  filter {
    name   = "tag:Env"
    values = [var.tags["Env"]]
  }
}

locals {
  vpc_id   = var.create_vpc ? aws_vpc.this[0].id : data.aws_vpc.shared[0].id
  vpc_cidr = var.create_vpc ? var.vpc_cidr : data.aws_vpc.shared[0].cidr_block
}

# Public subnets
resource "aws_subnet" "public" {
  count             = var.create_vpc ? var.az_count : 0
  vpc_id            = local.vpc_id
  cidr_block        = element(var.public_subnet_cidrs, count.index)
  availability_zone = element(local.azs, count.index)
  map_public_ip_on_launch = true
  tags = merge(var.tags, {
    Name = "${var.vpc_name}-public-${count.index}"
    Tier = "public"
  })
}

# Private subnets
resource "aws_subnet" "private" {
  count             = var.create_vpc ? var.az_count : 0
  vpc_id            = local.vpc_id
  cidr_block        = element(var.private_subnet_cidrs, count.index)
  availability_zone = element(local.azs, count.index)
  map_public_ip_on_launch = false
  tags = merge(var.tags, {
    Name = "${var.vpc_name}-private-${count.index}"
    Tier = "private"
  })
}

# Internet gateway for public access
resource "aws_internet_gateway" "igw" {
  count = var.create_vpc ? 1 : 0
  vpc_id = local.vpc_id
  tags   = merge(var.tags, { Name = "${var.vpc_name}-igw" })
}

# Route table for public subnets
resource "aws_route_table" "public" {
  count  = var.create_vpc ? 1 : 0
  vpc_id = local.vpc_id
  tags   = merge(var.tags, { Name = "${var.vpc_name}-public-rt" })
}

resource "aws_route" "public_internet" {
  count                  = var.create_vpc ? 1 : 0
  route_table_id         = aws_route_table.public[0].id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.igw[0].id
}

resource "aws_route_table_association" "public" {
  count          = var.create_vpc ? length(aws_subnet.public) : 0
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public[0].id
}

# NAT gateway and EIP. Only create when requested. If single_nat_gateway is true,
# create a single NAT in the first public subnet; otherwise one per AZ.
resource "aws_eip" "nat" {
  count  = var.create_vpc && var.single_nat_gateway ? 1 : var.create_vpc && !var.single_nat_gateway ? var.az_count : 0
  domain = "vpc"
  tags   = merge(var.tags, { Name = "${var.vpc_name}-nat-eip-${count.index}" })
}

resource "aws_nat_gateway" "nat" {
  count = length(aws_eip.nat)
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[ var.single_nat_gateway ? 0 : count.index ].id
  tags          = merge(var.tags, { Name = "${var.vpc_name}-nat-${count.index}" })

  depends_on = [aws_internet_gateway.igw]
}

# Route table for private subnets
resource "aws_route_table" "private" {
  count  = var.create_vpc ? (var.single_nat_gateway ? 1 : var.az_count) : 0
  vpc_id = local.vpc_id
  tags   = merge(var.tags, { Name = "${var.vpc_name}-private-rt-${count.index}" })
}

resource "aws_route" "private_nat" {
  count = var.create_vpc ? (var.single_nat_gateway ? var.az_count : var.az_count) : 0
  route_table_id         = aws_route_table.private[var.single_nat_gateway ? 0 : count.index].id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.nat[var.single_nat_gateway ? 0 : count.index].id
}

resource "aws_route_table_association" "private" {
  count = var.create_vpc ? var.az_count : 0
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[var.single_nat_gateway ? 0 : count.index].id
}

# VPC endpoints
resource "aws_vpc_endpoint" "s3" {
  count = var.create_vpc && var.enable_endpoints ? 1 : 0
  vpc_id       = local.vpc_id
  service_name = "com.amazonaws.${data.aws_region.current.name}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [for rt in aws_route_table.private : rt.id]
  tags = merge(var.tags, { Name = "${var.vpc_name}-s3-endpoint" })
}

data "aws_region" "current" {}

resource "aws_vpc_endpoint" "interface" {
  count = var.create_vpc && var.enable_endpoints ? length(local.interface_services) : 0
  vpc_id            = local.vpc_id
  service_name      = "com.amazonaws.${data.aws_region.current.name}.${element(local.interface_services, count.index)}"
  vpc_endpoint_type = "Interface"
  security_group_ids = [aws_security_group.endpoints[0].id]
  subnet_ids        = aws_subnet.private[*].id
  private_dns_enabled = true
  tags             = merge(var.tags, { Name = "${var.vpc_name}-${element(local.interface_services, count.index)}-endpoint" })
}

locals {
  interface_services = ["ecr.api", "ecr.dkr", "logs", "secretsmanager"]
}

resource "aws_security_group" "endpoints" {
  count = var.create_vpc && var.enable_endpoints ? 1 : 0
  name   = "${var.vpc_name}-endpoints-sg"
  vpc_id = local.vpc_id
  description = "Security group for VPC interface endpoints"
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    # Allow HTTPS access from all VPC resources (private subnets only)
    # This enables ECS tasks to access ECR, Secrets Manager, and CloudWatch Logs endpoints
    cidr_blocks = [local.vpc_cidr]
  }
  tags = var.tags
}

###############################################################################
# Data sources to pull existing VPC and subnets when create_vpc=false
###############################################################################

data "aws_subnets" "private" {
  count = var.create_vpc ? 0 : 1
  filter {
    name   = "tag:Tier"
    values = ["private"]
  }
  filter {
    name   = "vpc-id"
    values = [local.vpc_id]
  }
}

data "aws_subnets" "public" {
  count = var.create_vpc ? 0 : 1
  filter {
    name   = "tag:Tier"
    values = ["public"]
  }
  filter {
    name   = "vpc-id"
    values = [local.vpc_id]
  }
}

###############################################################################
# Outputs
###############################################################################

output "vpc_id" {
  value = local.vpc_id
}

output "public_subnet_ids" {
  value = var.create_vpc ? aws_subnet.public[*].id : data.aws_subnets.public[0].ids
}

output "private_subnet_ids" {
  value = var.create_vpc ? aws_subnet.private[*].id : data.aws_subnets.private[0].ids
}

output "nat_gateway_ids" {
  value = var.create_vpc ? aws_nat_gateway.nat[*].id : []
}

output "vpc_cidr" {
  value = local.vpc_cidr
}