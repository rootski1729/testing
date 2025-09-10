fix these High-impact gaps / risks -

No HTTPS anywhere.

ALB only has port 80; S3 website is HTTP-only. For prod, you’ll want TLS for both API and frontend.

Frontend is publicly readable S3.

With account-level S3 Block Public Access (commonly enabled), your site may still be blocked. Also, public ACLs are discouraged.

API likely lacks the Postgres password.

ECS task gets rds_endpoint but not the RDS password. Task role has no Secrets Manager permissions and the module doesn’t inject a secret. The app probably can’t auth to Postgres as-is.

ECR VPC endpoints probably unnecessary.

Your image is on GHCR. If you’re not pulling from ECR, those two interface endpoints add cost without benefit.

Single NAT gateway = single-AZ dependency.

Cost-efficient but an AZ outage can break egress for tasks in the other AZ.

Health check path

Target group checks GET /healthz on the container’s traffic port. Make sure the app serves that on :8000.

Encryption defaults (DocDB).

RDS is explicitly encrypted; DocDB’s storage_encrypted isn’t shown—double-check it’s enabled with a KMS key as intended.

ECS Exec disabled.

Consider enabling execute-command for on-box debugging in prod.

Recommended fixes (minimal edits)

API TLS at the ALB

Add an HTTPS listener (and redirect HTTP→HTTPS) to your ALB module when var.acm_certificate_arn is set:

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.this.arn
  port              = 443
  protocol          = "HTTPS"
  certificate_arn   = var.acm_certificate_arn
  default_action { type = "forward", target_group_arn = aws_lb_target_group.this.arn }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.this.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type = "redirect"
    redirect { port = "443", protocol = "HTTPS", status_code = "HTTP_301" }
  }
}


Frontend over HTTPS via CloudFront (and close public S3)

Set acm_certificate_arn (us-east-1) and update the frontend module to:

Use CloudFront + OAC.

Replace the public bucket policy with an OAC-scoped policy and enable S3 Block Public Access on the bucket.
Example bucket policy for OAC:

data "aws_caller_identity" "current" {}
resource "aws_s3_bucket_public_access_block" "this" {
  bucket                  = aws_s3_bucket.this.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

data "aws_iam_policy_document" "oac_read" {
  statement {
    sid     = "AllowCloudFrontOAC"
    actions = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.this.arn}/*"]
    principals { type = "Service", identifiers = ["cloudfront.amazonaws.com"] }
    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.this.arn]
    }
  }
}
resource "aws_s3_bucket_policy" "this" {
  bucket = aws_s3_bucket.this.id
  policy = data.aws_iam_policy_document.oac_read.json
}


Give the app a Postgres password
Pick one of these clean approaches:

Secrets Manager (recommended):

Create a secret from module.rds[0].password.

Attach an IAM policy to ECS task role allowing secretsmanager:GetSecretValue on that secret.

Pass it to the container via secrets in the task definition (not plain env vars).

IAM DB Auth: Enable on RDS and use IAM tokens; grant the task role rds-db:connect. (Adds some app changes.)

Plain env var: Quick but least safe—avoid in prod.

Drop unused endpoints (if staying on GHCR)

Remove the ECR interface endpoints to save cost, or move the image to ECR (then they make sense).

Post-apply checks

dig +short api-aps.hicaliber.net → resolves to the ALB; curl -I https://api-aps.hicaliber.net/healthz returns 200 (after HTTPS changes).

dig +short aps.hicaliber.net → CloudFront domain (if enabled) and serves the React app over HTTPS.

ECS service has 2 healthy targets in the ALB target group.

App connects to Postgres (verify logs) and DocumentDB.

S3 bucket is not public; content is only accessible via CloudFront.