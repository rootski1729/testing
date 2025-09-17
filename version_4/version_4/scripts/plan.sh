#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: $(basename "$0") --client <ClientName> --plan <SaaS|Dedicated> --env <stg|prod> --subdomain <subdomain> [options]

Options:
  --region <aws-region>               AWS region to deploy into (default: us-east-1)
  --acm-cert-arn <arn>                ACM certificate ARN for TLS termination
  --saas-docdb-uri <uri>              Shared SaaS DocumentDB connection string for SaaS tenants
  --saas-rds-endpoint <endpoint>      Shared SaaS PostgreSQL endpoint (host:port/dbname)
  --saas-api-lb-dns <dns>             Shared SaaS API ALB DNS name
  --saas-api-lb-zone <zone>           Shared SaaS API ALB hosted zone ID
  --frontend-bucket <bucket>          Override S3 bucket name for the frontend
  -h, --help                          Show this help message

Examples:
  # Plan a dedicated stack for Acme in staging
  $(basename "$0") --client Acme --plan Dedicated --env stg --subdomain acme

  # Plan a new SaaS tenant pointing at pre‑created shared infrastructure
  $(basename "$0") --client NewTenant --plan SaaS --env prod --subdomain saas-customer \
    --saas-docdb-uri mongodb://admin:pass@host:27017/?ssl=true\&replicaSet=rs0\&retryWrites=false \
    --saas-rds-endpoint host:5432/dbname --saas-api-lb-dns saas-api.example.com \
    --saas-api-lb-zone Z1234567890
USAGE
}

# Default values
REGION="us-east-1"
ACM_CERT=""
SAAS_DOCDB=""
SAAS_RDS=""
SAAS_LB_DNS=""
SAAS_LB_ZONE=""
FRONT_BUCKET=""

POSITIONAL=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --client)
      CLIENT="$2"
      shift 2
      ;;
    --plan)
      PLAN="$2"
      shift 2
      ;;
    --env)
      ENVIRONMENT="$2"
      shift 2
      ;;
    --subdomain)
      SUBDOMAIN="$2"
      shift 2
      ;;
    --region)
      REGION="$2"
      shift 2
      ;;
    --acm-cert-arn)
      ACM_CERT="$2"
      shift 2
      ;;
    --saas-docdb-uri)
      SAAS_DOCDB="$2"
      shift 2
      ;;
    --saas-rds-endpoint)
      SAAS_RDS="$2"
      shift 2
      ;;
    --saas-api-lb-dns)
      SAAS_LB_DNS="$2"
      shift 2
      ;;
    --saas-api-lb-zone)
      SAAS_LB_ZONE="$2"
      shift 2
      ;;
    --frontend-bucket)
      FRONT_BUCKET="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      usage
      exit 1
      ;;
  esac
done

if [[ -z "${CLIENT:-}" || -z "${PLAN:-}" || -z "${ENVIRONMENT:-}" || -z "${SUBDOMAIN:-}" ]]; then
  echo "Error: --client, --plan, --env and --subdomain are required"
  usage
  exit 1
fi

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT="${SCRIPT_DIR}/.."
cd "$PROJECT_ROOT"

TFVARS=(
  -var="client_name=${CLIENT}"
  -var="plan=${PLAN}"
  -var="env=${ENVIRONMENT}"
  -var="subdomain=${SUBDOMAIN}"
  -var="aws_region=${REGION}"
)

if [[ -n "$ACM_CERT" ]]; then
  TFVARS+=( -var="acm_certificate_arn=${ACM_CERT}" )
fi
if [[ -n "$SAAS_DOCDB" ]]; then
  TFVARS+=( -var="saas_documentdb_uri=${SAAS_DOCDB}" )
fi
if [[ -n "$SAAS_RDS" ]]; then
  TFVARS+=( -var="saas_rds_endpoint=${SAAS_RDS}" )
fi
if [[ -n "$SAAS_LB_DNS" ]]; then
  TFVARS+=( -var="saas_api_lb_dns_name=${SAAS_LB_DNS}" )
fi
if [[ -n "$SAAS_LB_ZONE" ]]; then
  TFVARS+=( -var="saas_api_lb_zone_id=${SAAS_LB_ZONE}" )
fi
if [[ -n "$FRONT_BUCKET" ]]; then
  TFVARS+=( -var="frontend_bucket_name=${FRONT_BUCKET}" )
fi

terraform init
terraform plan "${TFVARS[@]}"