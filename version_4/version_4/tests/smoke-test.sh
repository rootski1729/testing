#!/usr/bin/env bash
set -euo pipefail

# Simple smoke test for a Caliber deployment.  It waits for the ALB to
# report healthy targets, then checks the /healthz endpoint and reports
# success or failure.  You can run this after `terraform apply` to verify
# that the API is reachable and healthy.

usage() {
  cat <<'USAGE'
Usage: $(basename "$0") --subdomain <subdomain> [--region <aws-region>] [--timeout <seconds>]

Options:
  --region <aws-region>  AWS region where the ALB lives (default: us-east-1)
  --timeout <seconds>    How long to wait for healthy targets (default: 300)
  -h, --help             Show this help message

Example:
  ./smoke-test.sh --subdomain acme
USAGE
}

REGION="us-east-1"
TIMEOUT=300

while [[ $# -gt 0 ]]; do
  case "$1" in
    --subdomain)
      SUBDOMAIN="$2"
      shift 2
      ;;
    --region)
      REGION="$2"
      shift 2
      ;;
    --timeout)
      TIMEOUT="$2"
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

if [[ -z "${SUBDOMAIN:-}" ]]; then
  echo "Error: --subdomain is required"
  usage
  exit 1
fi

FQDN="${SUBDOMAIN}.hicaliber.net"

echo "Waiting for targets of ${FQDN} to become healthy..." >&2

# Resolve the load balancer DNS name from Route53 record.  We use dig to
# fetch the A record.  If dig is not available you may need to install it.
LB_DNS=$(dig +short "$FQDN" | head -n1)
if [[ -z "$LB_DNS" ]]; then
  echo "Unable to resolve $FQDN.  Ensure DNS propagation is complete."
  exit 1
fi

# Determine the target group ARN by listing all ALBs and matching the DNS
TG_ARN=$(aws --region "$REGION" elbv2 describe-load-balancers --query "LoadBalancers[?DNSName=='${LB_DNS}'] | [0].LoadBalancerArn" --output text)
if [[ "$TG_ARN" == "None" || -z "$TG_ARN" ]]; then
  echo "Could not find ALB for DNS $LB_DNS"
  exit 1
fi

TARGET_GROUP_ARN=$(aws --region "$REGION" elbv2 describe-target-groups --load-balancer-arn "$TG_ARN" --query 'TargetGroups[0].TargetGroupArn' --output text)

START=$(date +%s)
while true; do
  HEALTH=$(aws --region "$REGION" elbv2 describe-target-health --target-group-arn "$TARGET_GROUP_ARN" --query 'TargetHealthDescriptions[].TargetHealth.State' --output text | tr '\n' ' ')
  if [[ "$HEALTH" == *"healthy"* ]]; then
    echo "Targets healthy: $HEALTH" >&2
    break
  fi
  NOW=$(date +%s)
  if (( NOW - START > TIMEOUT )); then
    echo "Timed out waiting for healthy targets"
    exit 1
  fi
  sleep 5
done

echo "Performing HTTP health check on http://${FQDN}/healthz" >&2
if curl -fsS "http://${FQDN}/healthz" >/dev/null; then
  echo "Smoke test passed: ${FQDN} is healthy"
else
  echo "Smoke test failed: /healthz returned non‑OK response" >&2
  exit 1
fi