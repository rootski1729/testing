#!/usr/bin/env bash
set -euo pipefail

# This script seeds AWS Secrets Manager with connection details for the
# DocumentDB, PostgreSQL and a Django secret key.  It reads values from
# terraform outputs and writes them under a predictable Secrets Manager path.
#
# Usage:
#   ./seed-secrets.sh --client <ClientName> --env <stg|prod>
#                     [--prefix <base-prefix>] [--region <region>]
#
# The prefix determines where secrets will be stored.  By default secrets
# are stored under `caliber/<client-lower>/<env>`.

usage() {
  cat <<'USAGE'
Usage: $(basename "$0") --client <ClientName> --env <stg|prod> [options]

Options:
  --region <aws-region>  AWS region to operate in (default: us-east-1)
  --prefix <prefix>      Override the base prefix under which secrets are stored.
                         Default: caliber/<client-lower>/<env>
  -h, --help             Display this help message

The script reads terraform outputs `documentdb_uri` and `postgresql_endpoint` from
the current directory.  It requires AWS CLI with appropriate permissions to
manage Secrets Manager secrets.
USAGE
}

REGION="us-east-1"
PREFIX=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --client)
      CLIENT="$2"
      shift 2
      ;;
    --env)
      ENVIRONMENT="$2"
      shift 2
      ;;
    --region)
      REGION="$2"
      shift 2
      ;;
    --prefix)
      PREFIX="$2"
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

if [[ -z "${CLIENT:-}" || -z "${ENVIRONMENT:-}" ]]; then
  echo "Error: --client and --env are required"
  usage
  exit 1
fi

# Derive the default prefix if not provided.  Convert client name to lower
# case and strip spaces.
CLIENT_LOWER=$(echo "$CLIENT" | tr '[:upper:]' '[:lower:]' | tr -d ' ')
if [[ -z "$PREFIX" ]]; then
  PREFIX="caliber/${CLIENT_LOWER}/${ENVIRONMENT}"
fi

# Read terraform outputs.  Use terraform CLI to ensure values are pulled from
# the current state in this working directory.  `-raw` strips surrounding quotes.
DOCDB_URI=$(terraform output -raw documentdb_uri 2>/dev/null || true)
POSTGRES_ENDPOINT=$(terraform output -raw postgresql_endpoint 2>/dev/null || true)

if [[ -z "$DOCDB_URI" ]]; then
  echo "Warning: documentdb_uri output not found or empty.  Secrets for DocumentDB will not be created."
fi
if [[ -z "$POSTGRES_ENDPOINT" ]]; then
  echo "Warning: postgresql_endpoint output not found or empty.  Secrets for PostgreSQL will not be created."
fi

# Generate a Django secret key if none exists.  50 characters from /dev/urandom
generate_django_secret() {
  # Use Python to generate a random string avoiding shell cryptic char quoting
  python3 - <<'PY'
import os
import random
import string

chars = string.ascii_letters + string.digits + string.punctuation.replace('"', '').replace("'", '')
secret = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
print(secret)
PY
}

DJANGO_SECRET=$(generate_django_secret)

# Helper to create or update a secret
create_or_update_secret() {
  local name="$1"
  local secret_string="$2"
  local region="$3"
  if aws --region "$region" secretsmanager describe-secret --secret-id "$name" >/dev/null 2>&1; then
    # Secret exists, update value
    aws --region "$region" secretsmanager put-secret-value \
      --secret-id "$name" \
      --secret-string "$secret_string" >/dev/null
    echo "Updated secret $name"
  else
    aws --region "$region" secretsmanager create-secret \
      --name "$name" \
      --secret-string "$secret_string" >/dev/null
    echo "Created secret $name"
  fi
}

if [[ -n "$DOCDB_URI" ]]; then
  SECRET_NAME="${PREFIX}/documentdb"
  SECRET_PAYLOAD=$(jq -nc --arg uri "$DOCDB_URI" '{uri:$uri}')
  create_or_update_secret "$SECRET_NAME" "$SECRET_PAYLOAD" "$REGION"
fi

if [[ -n "$POSTGRES_ENDPOINT" ]]; then
  SECRET_NAME="${PREFIX}/postgresql"
  # Store the endpoint string as a simple JSON value.  You can expand this
  # structure to include user and password if desired.
  SECRET_PAYLOAD=$(jq -nc --arg endpoint "$POSTGRES_ENDPOINT" '{endpoint:$endpoint}')
  create_or_update_secret "$SECRET_NAME" "$SECRET_PAYLOAD" "$REGION"
fi

# Always store a Django secret key
SECRET_NAME="${PREFIX}/django"
SECRET_PAYLOAD=$(jq -nc --arg secret "$DJANGO_SECRET" '{secret:$secret}')
create_or_update_secret "$SECRET_NAME" "$SECRET_PAYLOAD" "$REGION"

echo "Secrets seeded under prefix $PREFIX"