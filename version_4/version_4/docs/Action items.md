Action items
ECR & ECS

Point the ECS task definition to the ECR image URI and pin by digest (…ecr.ap-south-1.amazonaws.com/<repo>@sha256:...), not :latest.

Keep/verify VPC endpoints for ECR API, ECR DKR, and S3 (Gateway) and ensure the S3 endpoint is attached to the private route tables.

Ensure the execution role has AmazonECSTaskExecutionRolePolicy; confirm the ECR repo policy allows pulls from this account.

Enable ECR image scanning and add a lifecycle policy to prune old tags.

API (ALB) – HTTPS

Request/attach an ACM cert in us-east-1 for api-aps.hicaliber.net.

Add an HTTPS :443 listener, and redirect :80 → :443.

Keep Route53 A/ALIAS for api-aps.hicaliber.net pointed at the ALB.

Frontend – HTTPS via CloudFront

Replace public S3 website with CloudFront + OAC (Origin Access Control).

Make the S3 bucket private and enable S3 Block Public Access.

Use an ACM cert for aps.hicaliber.net, and point Route53 to CloudFront (A/ALIAS).

Secrets & config

Move RDS and DocumentDB passwords to Secrets Manager; wire them into the ECS task definition secrets.

Grant the task role secretsmanager:GetSecretValue scoped to those ARNs (execution role already covers pull/logging).

Databases

RDS (PostgreSQL): inbound only from the ECS service SG; Multi-AZ and deletion protection enabled; backups retained (30d).

DocumentDB: ensure encryption at rest (KMS); SG inbound only from ECS SG; verify the app’s connection string flags (TLS, replica set, retryable writes as required).

Reliability & ops

Enable ECS deployment circuit breaker with rollback.

Keep desired count = 2 and add Application Auto Scaling on CPU/Memory.

Turn on ALB access logs to S3.

Add CloudWatch alarms: ALB 5XX, Target Group UnhealthyHostCount, ECS Task failures/CrashLoop, RDS/DocDB CPU/FreeStorage/Connections.

Network & security

Security groups:

ALB: inbound 80/443 from 0.0.0.0/0.

ECS service: inbound 8000 from ALB SG only.

RDS & DocDB: inbound from ECS SG only.

Consider one NAT Gateway per AZ (currently single NAT) for HA.

Attach AWS WAFv2 to ALB (and/or CloudFront) with AWS managed rules.

Confirm health check GET /healthz on port 8000 (ALB TG path).

Deliverables

Terraform PR implementing the above, with a plan preview.

After apply: share ALB DNS, CloudFront distribution ID/URL, and Secrets Manager ARNs.