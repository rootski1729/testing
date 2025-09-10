Fixes the following issues / bugs which we currently have - 

Duplicate DNS name for API and frontend

aws_route53_record.api and aws_route53_record.frontend both create aps.hicaliber.net. Route 53 cannot have a CNAME and an A-alias with the same name.

Fix: keep frontend at aps.hicaliber.net and move API to api-aps.hicaliber.net (or vice versa). Create separate records.

Open security groups to the world

DocumentDB SG allows 0.0.0.0/0 on 27017: module.docdb[0].aws_security_group.this.

RDS SG allows 0.0.0.0/0 on 5432: module.rds[0].aws_security_group.this.

ECS service SG allows 0.0.0.0/0 on 8000: module.compute[0].aws_security_group.this.

Fix: restrict DB SG ingress to the ECS service SG, and ECS SG ingress to the ALB SG only.

No HTTPS anywhere for the app

ALB listener is HTTP 80 only: module.alb[0].aws_lb_listener.http.

Frontend falls back to S3 website hosting with acl = public-read and no CloudFront or certs. S3 website endpoints do not support HTTPS for custom domains.

Fix: always terminate TLS, either

CloudFront + OAC in front of S3, with ACM cert, and

ALB HTTPS listener on 443 with ACM cert and an HTTP 80 redirect to 443.

Likely apply failures or hidden footguns

VPC endpoint SG ingress has no source

module.network.aws_security_group.endpoints[0] shows ingress on 443 without cidr_blocks or security_groups. That is invalid.

Fix: set cidr_blocks = [var.vpc_cidr] for that ingress rule.

Public S3 website for frontend

module.frontend.aws_s3_bucket.this has acl = public-read and a public bucket policy. This breaks the security posture and blocks HTTPS at the vanity domain.

Fix: require CloudFront + OAC, make bucket private, block public access.

Sensitive output exposed

Root output documentdb_uri is not marked sensitive.

Fix: output "documentdb_uri" { sensitive = true }. Also, write credentials to Secrets Manager and inject via task definition, not outputs.

Bucket name collision risk

aps-prod-dedicated-frontend may not be globally unique.

Fix: include account id or a short random suffix in the bucket name.

High priority hardening

ALB hardening

Enable HTTPS listener with ACM, add HTTP to HTTPS redirect rule.

Turn on access logs to S3.

Consider drop_invalid_header_fields = true.

DB deletion safety

skip_final_snapshot = true and deletion_protection = null on both RDS and DocumentDB. Not acceptable for prod.

Fix: deletion_protection = true, skip_final_snapshot = false in prod, set backup windows and retention explicitly.

Overprovisioned DocumentDB

Instance class db.r6g.large for CRUD at 20 to 100 RPS is probably overkill and expensive.

Fix: start with db.t4g.medium or consider DocumentDB Serverless with min capacity.

NAT gateway single AZ tradeoff

single_nat_gateway = true saves cost but introduces an AZ dependency.

Fix: acceptable for stg, but document the prod risk or allow a toggle to one-per-az.

Medium priority improvements

ECS deployment safety

wait_for_steady_state = false, no deployment circuit breaker.

Fix: set deployment_circuit_breaker { enable = true, rollback = true } and wait for steady state in CI.

RDS observability

enabled_cloudwatch_logs_exports is null.

Fix: enable postgresql logs you care about and set retention.

Secrets lifecycle

Passwords are generated but not stored in Secrets Manager.

Fix: create Secrets Manager entries per client and reference them in task defs.

ALB preserve Host header

For subdomain based auth, Host must reach Django. ALB already forwards Host for HTTP, but be explicit if you later put NLB or proxies in path.