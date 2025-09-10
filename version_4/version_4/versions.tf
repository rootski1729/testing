terraform {
  required_version = "= 1.13.1"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}

# Configure the AWS provider. Region is supplied via variable or environment
# variables; defaulting here to allow local use. The provider will pick up
# credentials from the environment or from a configured profile. See docs
# for details.
provider "aws" {
  region = var.aws_region
}

# Additional provider for CloudFront certificates (must be in us-east-1)
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}