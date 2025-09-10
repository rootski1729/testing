#!/usr/bin/env bash
set -euo pipefail

# Trigger a zero‑downtime rollout of the API service by forcing a new ECS
# deployment.  This will launch new tasks and then stop the old ones once
# healthy.  Use this script after updating the container image or when you
# need to pick up new secrets.

usage() {
  cat <<'USAGE'
Usage: $(basename "$0") --client <ClientName> --plan <SaaS|Dedicated> --env <stg|prod> [options]

Options:
  --region <aws-region>  AWS region where ECS is deployed (default: us-east-1)
  -h, --help             Show this help message

Example:
  ./rollout-api.sh --client Acme --plan Dedicated --env stg
USAGE
}

REGION="us-east-1"
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
    --region)
      REGION="$2"
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

if [[ -z "${CLIENT:-}" || -z "${PLAN:-}" || -z "${ENVIRONMENT:-}" ]]; then
  echo "Error: --client, --plan and --env are required"
  usage
  exit 1
fi

CLIENT_LOWER=$(echo "$CLIENT" | tr '[:upper:]' '[:lower:]' | tr -d ' ')
PLAN_LOWER=$(echo "$PLAN" | tr '[:upper:]' '[:lower:]')
NAME_PREFIX="${CLIENT_LOWER}-${ENVIRONMENT}-${PLAN_LOWER}"
CLUSTER_NAME="${NAME_PREFIX}-cluster"
SERVICE_NAME="${CLUSTER_NAME}-service"

echo "Forcing new deployment for service ${SERVICE_NAME} in cluster ${CLUSTER_NAME}" >&2

aws --region "$REGION" ecs update-service \
  --cluster "$CLUSTER_NAME" \
  --service "$SERVICE_NAME" \
  --force-new-deployment >/dev/null

echo "Deployment triggered.  ECS will roll out new tasks and drain old ones."