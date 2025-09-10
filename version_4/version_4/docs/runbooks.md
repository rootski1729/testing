# Operational runbooks

This document provides procedures for operating the Caliber infrastructure.  Each runbook is self contained and can be followed by an engineer with basic AWS and Terraform knowledge.

## 1. First deploy per client

Follow these steps when provisioning a new client.  The process differs slightly for **Dedicated** and **SaaS** tenants.

### 1.1 Dedicated client

1. **Plan and apply:**

   ```sh
   cd project_caliber_infra
   ./scripts/init.sh
   ./scripts/plan.sh  --client Acme --plan Dedicated --env stg --subdomain acme
   ./scripts/apply.sh --client Acme --plan Dedicated --env stg --subdomain acme
   ```

   This command creates a new VPC with one NAT gateway and VPC endpoints, a DocumentDB cluster (private), a PostgreSQL instance (private), an ECS cluster and service, an ALB, a static site bucket and CloudFront distribution, and two Route 53 records: `acme.hicaliber.net` (API) and `www.acme.hicaliber.net` (frontend).

2. **Seed secrets:**

   ```sh
   ./scripts/seed-secrets.sh --client Acme --env stg
   ```

   This script reads the DocumentDB connection URI and PostgreSQL endpoint from Terraform outputs and stores them, along with a randomly generated Django secret key, in AWS Secrets Manager under `caliber/acme/stg/…`.

3. **Migrate databases:**

   ```sh
   ./scripts/migrate.sh --client Acme --plan Dedicated --env stg
   ```

   A one off Fargate task runs `python manage.py migrate` using the same task definition as the API.

4. **Roll out the API:**

   ```sh
   ./scripts/rollout-api.sh --client Acme --plan Dedicated --env stg
   ```

   Forces a new ECS deployment so that containers pick up the newly seeded secrets and run the latest code.

5. **Deploy the frontend:**

   ```sh
   npm run build
   ./scripts/deploy-frontend.sh --client Acme --plan Dedicated --env stg --build-dir ./build
   ```

   Syncs the build directory to the S3 bucket and invalidates CloudFront.

6. **Run smoke test:**

   ```sh
   ./tests/smoke-test.sh --subdomain acme
   ```

### 1.2 SaaS shared stack (SaaSShared)

1. Provision the shared infrastructure once.  The client name **must** be `SaaSShared`:

   ```sh
   ./scripts/apply.sh --client SaaSShared --plan SaaS --env stg --subdomain saas-api
   ```

   This creates a shared VPC, DocumentDB cluster and PostgreSQL instance, ECS cluster and ALB.  Make note of the outputs: `documentdb_uri`, `postgresql_endpoint`, `api_endpoint` and `frontend_url`.

2. Seed and migrate as above, replacing `Acme` with `SaaSShared`.

### 1.3 SaaS tenant

For each additional tenant, reuse the shared infrastructure by supplying the endpoints from the shared stack:

```sh
./scripts/apply.sh \
  --client NewTenant \
  --plan SaaS \
  --env stg \
  --subdomain customer1 \
  --saas-docdb-uri    <documentdb_uri from SaaSShared> \
  --saas-rds-endpoint <postgresql_endpoint from SaaSShared> \
  --saas-api-lb-dns   <api_endpoint from SaaSShared> \
  --saas-api-lb-zone  <hosted_zone_id from SaaSShared>
```

Then seed secrets, run migrations, roll out the API and deploy the frontend using the same scripts, specifying `--plan SaaS`.

## 2. Rollback

To roll back an API deployment (for example, if a new image introduces an issue):

1. Identify the previous task definition ARN for the service:

   ```sh
   aws ecs list-task-definitions --family-prefix <cluster-name> --status ACTIVE --sort DESC
   ```

2. Update the service to use the previous task definition:

   ```sh
   aws ecs update-service --cluster <cluster-name> --service <service-name> --task-definition <previous-task-def-arn>
   ```

3. Monitor the deployment in the ECS console or via `aws ecs describe-services` until the older tasks are running and healthy.

For database rollbacks, restore from snapshots (see section 4).

## 3. Rotate secrets

When rotating database passwords or the Django secret key:

1. Update the secret values in Secrets Manager.  You can generate new credentials manually or let AWS rotate them if using automatic rotation.

2. Re run the seed script to update the path used by the application:

   ```sh
   ./scripts/seed-secrets.sh --client Acme --env stg
   ```

3. Force a new deployment so containers fetch the updated secrets:

   ```sh
   ./scripts/rollout-api.sh --client Acme --plan Dedicated --env stg
   ```

## 4. Restore a database

### 4.1 Restore Amazon DocumentDB

Amazon DocumentDB supports point in time restore.  To restore to a new cluster:

1. Identify the ARN of the cluster snapshot or the point in time to restore to.  Use `aws docdb describe-db-cluster-snapshots`.

2. Restore the snapshot:

   ```sh
   aws docdb restore-db-cluster-to-point-in-time \
     --db-cluster-identifier <new-cluster-id> \
     --source-db-cluster-identifier <original-cluster-id> \
     --restore-to-time <ISO8601 timestamp>
   ```

3. Update the Terraform state or variables to point the application at the new cluster endpoint.

### 4.2 Restore PostgreSQL

RDS automated backups are enabled with a seven day retention【473073595576958†L90-L99】.  To restore:

1. List available snapshots:

   ```sh
   aws rds describe-db-snapshots --db-instance-identifier <instance-id>
   ```

2. Restore the snapshot to a new instance:

   ```sh
   aws rds restore-db-instance-from-db-snapshot \
     --db-instance-identifier <new-instance-id> \
     --db-snapshot-identifier <snapshot-id> \
     --db-subnet-group-name <subnet-group> \
     --vpc-security-group-ids <security-group-id>
   ```

3. Update the application secrets to use the new endpoint and roll out the API as in section 3.

## 5. Add a new client

Use the `apply.sh` wrapper to add clients.  No code changes are necessary; specify only the variables.  See examples in the quickstart.  For SaaS tenants, always pass the endpoints from the `SaaSShared` outputs.

## 6. Decommission a client

Run the `destroy.sh` script with the same arguments used for apply.  Production environments require the `--force` flag to prevent accidental deletion:

```sh
./scripts/destroy.sh --client Acme --plan Dedicated --env prod --subdomain acme --force
```

Ensure that you have taken backups of databases and that no other tenants depend on shared resources.