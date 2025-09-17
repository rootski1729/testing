#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: $(basename "$0") --client <ClientName> --plan <SaaS|Dedicated> --env <stg|prod> --subdomain <subdomain> [options] [--force]

Options are identical to plan.sh and apply.sh. Destroying a production
environment requires an explicit --force flag to prevent accidental teardown.
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
FORCE=false

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
    --force)
      FORCE=true
      shift 1
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

# Prevent accidental destruction of production unless force flag is provided
if [[ "$ENVIRONMENT" == "prod" && "$FORCE" != true ]]; then
  echo "Refusing to destroy production environment without --force flag."
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
terraform destroy -auto-approve "${TFVARS[@]}"