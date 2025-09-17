output "security_group_id" {
  description = "Security group ID for the ECS service"
  value       = aws_security_group.this.id
}