locals {
  execution_role_name = "${var.cluster_name}-exec-role"
  task_role_name      = "${var.cluster_name}-task-role"
}

data "aws_region" "current" {}

# ECS cluster
resource "aws_ecs_cluster" "this" {
  name = var.cluster_name
  tags = var.tags
}

# IAM role for ECS tasks to pull images and write logs
resource "aws_iam_role" "exec" {
  name = local.execution_role_name
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json
  tags = var.tags
}

data "aws_iam_policy_document" "ecs_task_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role_policy_attachment" "exec_default" {
  role       = aws_iam_role.exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Additional policy to allow reading from Secrets Manager
# Always create the policy but with conditional resources to avoid count issues
locals {
  secret_arns = compact([var.docdb_secret_arn, var.rds_secret_arn])
  # If no secrets are provided, use a dummy ARN that won't match anything
  policy_resources = length(local.secret_arns) > 0 ? local.secret_arns : ["arn:aws:secretsmanager:*:*:secret:dummy-placeholder-*"]
}

resource "aws_iam_role_policy" "secrets_policy" {
  name   = "${local.execution_role_name}-secrets"
  role   = aws_iam_role.exec.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = local.policy_resources
      }
    ]
  })
}

# Task role for the container (minimal for now)
resource "aws_iam_role" "task" {
  name               = local.task_role_name
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json
  tags               = var.tags
}

# Security group for ECS tasks
resource "aws_security_group" "this" {
  name        = "${var.cluster_name}-svc-sg"
  description = "Allow inbound traffic from ALB only"
  vpc_id      = var.vpc_id
  ingress {
    from_port       = var.container_port
    to_port         = var.container_port
    protocol        = "tcp"
    security_groups = [var.alb_security_group_id]
  }
  # Allow HTTP and HTTPS to any API/service
  egress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # Allow common service ports (database, cache, message queues, etc.)
  egress {
    from_port   = 1024
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # Allow DNS queries for external domain resolution
  egress {
    from_port   = 53
    to_port     = 53
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 53
    to_port     = 53
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = var.tags
}

# ECS task definition (Fargate)
data "aws_iam_policy_document" "logging" {
  statement {
    effect = "Allow"
    actions = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["*"]
  }
}

resource "aws_ecs_task_definition" "this" {
  family                   = var.cluster_name
  cpu                      = "512"
  memory                   = "1024"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.exec.arn
  task_role_arn            = aws_iam_role.task.arn
  container_definitions    = jsonencode([
    {
      name         = "api"
      image        = var.image
      essential    = true
      portMappings = [ {
        containerPort = var.container_port
        hostPort      = var.container_port
        protocol      = "tcp"
      } ]
      environment   = concat([
        { name = "DJANGO_SETTINGS_MODULE", value = "caliber.settings" }
      ],
        var.docdb_secret_arn == "" ? [
          { name = "MONGO_URI", value = var.documentdb_uri }
        ] : [],
        var.rds_secret_arn == "" ? [
          { name = "DATABASE_URL", value = "postgresql://${var.rds_endpoint}" }
        ] : []
      )
      secrets = concat(
        var.docdb_secret_arn != "" ? [
          {
            name      = "MONGO_USERNAME"
            valueFrom = "${var.docdb_secret_arn}:username::"
          },
          {
            name      = "MONGO_PASSWORD"
            valueFrom = "${var.docdb_secret_arn}:password::"
          }
        ] : [],
        var.rds_secret_arn != "" ? [
          {
            name      = "RDS_USERNAME"
            valueFrom = "${var.rds_secret_arn}:username::"
          },
          {
            name      = "RDS_PASSWORD"
            valueFrom = "${var.rds_secret_arn}:password::"
          }
        ] : []
      )
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/aws/ecs/${var.cluster_name}"
          awslogs-region        = data.aws_region.current.name
          awslogs-stream-prefix = "api"
        }
      }
    }
  ])
  tags = var.tags
}

resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/ecs/${var.cluster_name}"
  retention_in_days = 30
  tags              = var.tags
}

# ECS service
resource "aws_ecs_service" "this" {
  name            = "${var.cluster_name}-service"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.this.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"
  network_configuration {
    subnets         = var.subnets
    security_groups = [aws_security_group.this.id]
    assign_public_ip = false
  }
  load_balancer {
    target_group_arn = var.alb_target_group
    container_name   = "api"
    container_port   = var.container_port
  }
  deployment_controller {
    type = "ECS"
  }
  deployment_maximum_percent = 200
  deployment_minimum_healthy_percent = 50
  propagate_tags = "SERVICE"
  tags = var.tags
  depends_on = [aws_cloudwatch_log_group.this]
}

# Application Auto Scaling for ECS Service
resource "aws_appautoscaling_target" "ecs_target" {
  max_capacity       = 3
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.this.name}/${aws_ecs_service.this.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# Auto Scaling Policy - CPU Utilization
resource "aws_appautoscaling_policy" "cpu_scaling" {
  name               = "${var.cluster_name}-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# Auto Scaling Policy - Memory Utilization
resource "aws_appautoscaling_policy" "memory_scaling" {
  name               = "${var.cluster_name}-memory-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value       = 80.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

output "cluster_id" {
  value = aws_ecs_cluster.this.id
}

output "service_name" {
  value = aws_ecs_service.this.name
}