#!/usr/bin/env bash
set -euo pipefail

# Deploy a built React frontend to the S3 bucket and invalidate the
# CloudFront cache if necessary.  The bucket name is derived from the
# Terraform naming convention unless overridden.  After uploading, the
# distribution is invalidated to ensure end users see the latest content.

usage() {
  cat <<'USAGE'
Usage: $(basename "$0") --client <ClientName> --plan <SaaS|Dedicated> --env <stg|prod> --build-dir <path> [options]

Options:
  --region <aws-region>    AWS region where the bucket exists (default: us-east-1)
  --bucket <bucket-name>   Override the S3 bucket name (rarely needed)
  -h, --help               Show this help message

Example:
  ./deploy-frontend.sh --client Acme --plan Dedicated --env prod --build-dir ./frontend/build
USAGE
}

REGION="us-east-1"
BUCKET=""

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
    --build-dir)
      BUILD_DIR="$2"
      shift 2
      ;;
    --region)
      REGION="$2"
      shift 2
      ;;
    --bucket)
      BUCKET="$2"
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

if [[ -z "${CLIENT:-}" || -z "${PLAN:-}" || -z "${ENVIRONMENT:-}" || -z "${BUILD_DIR:-}" ]]; then
  echo "Error: --client, --plan, --env and --build-dir are required"
  usage
  exit 1
fi

CLIENT_LOWER=$(echo "$CLIENT" | tr '[:upper:]' '[:lower:]' | tr -d ' ')
PLAN_LOWER=$(echo "$PLAN" | tr '[:upper:]' '[:lower:]')
NAME_PREFIX="${CLIENT_LOWER}-${ENVIRONMENT}-${PLAN_LOWER}"

if [[ -z "$BUCKET" ]]; then
  BUCKET="${NAME_PREFIX}-frontend"
fi

if [[ ! -d "$BUILD_DIR" ]]; then
  echo "Build directory $BUILD_DIR does not exist."
  exit 1
fi

echo "Uploading contents of $BUILD_DIR to s3://$BUCKET" >&2
aws --region "$REGION" s3 sync "$BUILD_DIR" "s3://${BUCKET}" --delete

# Attempt to invalidate CloudFront cache if a distribution is defined in outputs
DIST_ID=$(terraform output -raw frontend_distribution_id 2>/dev/null || true)
if [[ -n "$DIST_ID" ]]; then
  echo "Creating CloudFront invalidation for distribution $DIST_ID" >&2
  aws --region "$REGION" cloudfront create-invalidation --distribution-id "$DIST_ID" --paths '/*' >/dev/null
  echo "Invalidation submitted."
fi

echo "Frontend deployment complete."