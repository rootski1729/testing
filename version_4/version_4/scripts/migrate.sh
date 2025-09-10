#!/usr/bin/env bash
set -euo pipefail

# Run Django database migrations in a one‑off ECS Fargate task.  This script
# derives the ECS cluster and service names from the client, plan and env
# parameters, then launches a task overriding the command to run
# `python manage.py migrate`.

usage() {
  cat <<'USAGE'
Usage: $(basename "$0") --client <ClientName> --plan <SaaS|Dedicated> --env <stg|prod> [options]

Options:
  --region <aws-region>  AWS region where ECS is deployed (default: us-east-1)
  -h, --help             Show this help message

Example:
  ./migrate.sh --client Acme --plan Dedicated --env prod

This script assumes that the API container image includes the Django code
and that running `python manage.py migrate` inside the container will apply
database migrations.
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

# Derive cluster and service names based on Terraform naming convention.  The
# cluster name is lower(client)‑env‑lower(plan)-cluster.  Service name is the
# cluster name followed by -service.
CLIENT_LOWER=$(echo "$CLIENT" | tr '[:upper:]' '[:lower:]' | tr -d ' ')
PLAN_LOWER=$(echo "$PLAN" | tr '[:upper:]' '[:lower:]')
NAME_PREFIX="${CLIENT_LOWER}-${ENVIRONMENT}-${PLAN_LOWER}"
CLUSTER_NAME="${NAME_PREFIX}-cluster"
SERVICE_NAME="${CLUSTER_NAME}-service"

echo "Running migrations on cluster ${CLUSTER_NAME} (service ${SERVICE_NAME}) in region ${REGION}" >&2

# Fetch the service description to derive task definition and network config
SERVICE_JSON=$(aws --region "$REGION" ecs describe-services \
  --cluster "$CLUSTER_NAME" --services "$SERVICE_NAME" --output json)

TASK_DEFINITION=$(echo "$SERVICE_JSON" | jq -r '.services[0].taskDefinition')
SUBNETS=$(echo "$SERVICE_JSON" | jq -r '.services[0].networkConfiguration.awsvpcConfiguration.subnets | join(",")')
SGS=$(echo "$SERVICE_JSON" | jq -r '.services[0].networkConfiguration.awsvpcConfiguration.securityGroups | join(",")')

if [[ "$TASK_DEFINITION" == "null" || -z "$SUBNETS" ]]; then
  echo "Failed to retrieve ECS service details. Ensure the service exists and you have permission." >&2
  exit 1
fi

echo "Using task definition ${TASK_DEFINITION}" >&2

# Run the migration task
aws --region "$REGION" ecs run-task \
  --cluster "$CLUSTER_NAME" \
  --task-definition "$TASK_DEFINITION" \
  --launch-type FARGATE \
  --count 1 \
  --overrides '{"containerOverrides":[{"name":"api","command":["/bin/sh","-c","python manage.py migrate"]}]}' \
  --network-configuration "awsvpcConfiguration={subnets=[${SUBNETS}],securityGroups=[${SGS}],assignPublicIp=DISABLED}"

echo "Migration task started.  Use AWS ECS console or CLI to view progress."