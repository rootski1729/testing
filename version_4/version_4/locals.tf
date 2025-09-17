locals {
  # Lowercase client name to use in resource names
  client_lower = lower(replace(var.client_name, " ", ""))

  # Whether this is a production environment
  is_prod = var.env == "prod"

  # Baseline tags applied to all resources. Individual modules merge their own
  # service‑specific tags onto this map. Use the `Client` tag to separate per
  # customer resources, or the literal string "SaaSShared" for shared SaaS
  # infrastructure.
  base_tags = merge({
    Project   = "Caliber",
    Client    = var.plan == "SaaS" && var.client_name != "SaaSShared" ? "SaaSShared" : var.client_name,
    Plan      = var.plan,
    Env       = var.env,
    ManagedBy = "Terraform"
  }, var.tags)

  # Derive the fully qualified domain names for this deployment. We assume
  # the apex domain is hicaliber.net and that you control the hosted zone.
  # Separate API and frontend domains to avoid Route53 conflicts.
  api_fqdn = "api-${var.subdomain}.hicaliber.net"
  frontend_fqdn = "${var.subdomain}.hicaliber.net"
  
  # Main FQDN (for backwards compatibility)
  fqdn = local.frontend_fqdn

  # Derive a predictable prefix for resource names. AWS resource names must be
  # unique within the account/region, so include env and plan.
  name_prefix = join("-", [local.client_lower, var.env, lower(var.plan)])
}