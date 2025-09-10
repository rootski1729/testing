# Project Caliber Infrastructure

This repository defines a complete, self service infrastructure for the **Caliber** AI insurance platform.  It uses **Terraform v1.13.1** to create and manage AWS resources with zero downtime deployments.  The design supports two modes:

* **Dedicated** - A fully isolated stack per client, including its own VPC, DocumentDB cluster, PostgreSQL instance, ECS cluster and ALB.
* **SaaS** - A shared multi tenant stack for many clients.  A special tenant called `SaaSShared` provisions the shared networking, databases and compute.  Additional SaaS tenants reuse these shared resources by supplying the shared endpoints as inputs.

All resources are tagged with the following keys: `Project=Caliber`, `Client`, `Plan`, `Env` and `ManagedBy=Terraform`.  This allows cost allocation and automated cleanup.  The source domain `hicaliber.net` must be owned in Route 53.

The Terraform code follows best practices:

* DocumentDB is deployed in private subnets with TLS enabled, replica set `rs0` and `retryWrites=false` in the connection string, as recommended for Amazon DocumentDB【158328826106302†L64-L90】.  The module outputs a ready to use URI.
* RDS PostgreSQL instances live in private subnets with automated backups enabled (seven day retention) for durability【212798777614025†L92-L104】【473073595576958†L90-L99】.
* Networking uses a single NAT gateway per VPC and VPC endpoints for S3, ECR, CloudWatch Logs and Secrets Manager to reduce NAT charges【958022616469563†L160-L180】.
* Compute runs on ECS Fargate behind an ALB with health checks on `/healthz`.  The Host header is preserved end to end so that the Django API can authenticate based on subdomain.
* The React front end is served from an S3 bucket with optional CloudFront distribution for TLS and caching.
* GitHub Actions authenticate to AWS using OpenID Connect (OIDC) instead of long lived keys【708626089702406†L286-L330】【708626089702406†L441-L458】.

## Repository structure

```
project_caliber_infra/
├── modules/           # Reusable Terraform modules (network, DocumentDB, RDS, ALB, compute, frontend)
├── scripts/           # Wrapper scripts to operate on the infrastructure
├── tests/             # Smoke test script
├── docs/              # This documentation and runbooks
├── main.tf            # Orchestration of modules and Route 53 records
├── variables.tf       # Input variables
├── locals.tf          # Derived values and naming conventions
├── outputs.tf         # Useful outputs (endpoints and distribution id)
└── versions.tf        # Pinned provider and Terraform versions
```

## Prerequisites

* An AWS account with the `hicaliber.net` hosted zone in Route 53.
* [Terraform 1.13.1](https://terraform.io/) installed locally.
* [AWS CLI](https://aws.amazon.com/cli/) configured, or GitHub Actions configured for OIDC.
* `jq` and `dig` installed for the helper scripts.
* For CI, enable the GitHub OIDC identity provider in AWS and create an IAM role that trusts `token.actions.githubusercontent.com`【708626089702406†L286-L330】.

## Quickstart

1. **Clone the repo and change into the directory:**

   ```sh
   git clone <this-repo>
   cd project_caliber_infra
   ```

2. **Initialize Terraform:**

   ```sh
   ./scripts/init.sh
   ```

3. **Plan and apply infrastructure.**  You must specify the client name, plan, environment and subdomain.  The subdomain becomes the API host (e.g. `acme.hicaliber.net`) and a `www.` prefix is used for the frontend (e.g. `www.acme.hicaliber.net`).

   ### Dedicated example

   ```sh
   # Plan an isolated staging stack for Acme
   ./scripts/plan.sh   --client APS --plan Dedicated --env prod --subdomain aps

   # Apply the stack (creates VPC, DocDB, RDS, ECS, ALB, S3/CloudFront and DNS)
   ./scripts/apply.sh  --client Acme --plan Dedicated --env prod --subdomain acme
   ```

   ### SaaS shared infrastructure

   ```sh
   # Provision the shared SaaS infrastructure once.  The client name **must** be SaaSShared.
   ./scripts/apply.sh --client SaaSShared --plan SaaS --env prod --subdomain saas-api
   ```

   ### Add a new SaaS tenant

   After the shared stack exists, you can add tenants without modifying any code.  Provide the endpoints from the shared outputs as inputs:

   ```sh
   ./scripts/apply.sh \
     --client NewTenant \
     --plan SaaS \
     --env prod \
     --subdomain customer1 \
     --saas-docdb-uri       <DocumentDB connection URI from SaaSShared> \
     --saas-rds-endpoint    <PostgreSQL endpoint from SaaSShared> \
     --saas-api-lb-dns      <API ALB DNS from SaaSShared> \
     --saas-api-lb-zone     <API ALB zone ID from SaaSShared>
   ```

4. **Seed secrets.**  After `terraform apply` you should populate AWS Secrets Manager with your database endpoints and a Django secret key.  This ensures the API containers can retrieve credentials at runtime:

   ```sh
   ./scripts/seed-secrets.sh --client Acme --env prod
   ```

5. **Run database migrations:**

   ```sh
   ./scripts/migrate.sh --client Acme --plan Dedicated --env prod
   ```

6. **Roll out the API:**  If you change environment variables, secrets or update your container image, force a new deployment:

   ```sh
   ./scripts/rollout-api.sh --client Acme --plan Dedicated --env prod
   ```

7. **Deploy the frontend:**  Build your React application locally, then sync it to S3 and invalidate CloudFront:

   ```sh
   npm run build                # or yarn build
   ./scripts/deploy-frontend.sh --client Acme --plan Dedicated --env prod --build-dir ./build
   ```

8. **Run a smoke test:**

   ```sh
   ./tests/smoke-test.sh --subdomain acme
   ```

To destroy a stack, run the `destroy.sh` wrapper.  Destroying production requires the `--force` flag to avoid accidental data loss:

```sh
./scripts/destroy.sh --client Acme --plan Dedicated --env prod --subdomain acme
./scripts/destroy.sh --client Acme --plan Dedicated --env prod --subdomain acme --force
```

## Continuous integration

Two sample GitHub Actions workflows are provided in `.github/workflows`:

* **`ci-plan.yml`** - Runs `terraform plan` on pull requests and comments the plan summary.  It uses GitHub OIDC to authenticate to AWS.  No long-lived AWS secrets are stored.  To enable, create an IAM role with a trust policy that accepts the `token.actions.githubusercontent.com` provider with audience `sts.amazonaws.com`【708626089702406†L286-L330】.
* **`ci-apply.yml`** - Performs a manual `terraform apply` on pushes to the `main` branch after human approval.  It limits execution to the `infra` directory and uses the same OIDC role.  You can restrict the IAM role to specific actions (creating, updating and deleting resources) following the principle of least privilege.

## Known limitations and improvements

* The compute and database security groups currently allow traffic from any IP within the VPC.  You may refine these rules to only allow traffic from the ALB or ECS tasks.
* Secrets are stored via a helper script instead of Terraform resources to avoid leaking plaintext credentials in the state file.  You can move secrets creation into Terraform using `aws_secretsmanager_secret_version` if preferred.
* Backend database snapshots and point in time restore are enabled by default.  See the runbooks for detailed restore procedures.

Refer to the [runbooks](runbooks.md) for operational guidance.