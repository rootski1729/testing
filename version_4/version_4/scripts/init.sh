#!/usr/bin/env bash
set -euo pipefail

# This script initializes the Terraform working directory. It should be run
# before planning or applying. Use the TF_IN_AUTOMATION environment variable
# when running in CI to disable interactive prompts.

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT="${SCRIPT_DIR}/.."

cd "$PROJECT_ROOT"

terraform init "$@"