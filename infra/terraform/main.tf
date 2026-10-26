data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

data "aws_partition" "current" {}

locals {
  availability_zones = slice(data.aws_availability_zones.available.names, 0, 2)
  public_subnets = {
    for index, cidr in ["10.42.0.0/24", "10.42.1.0/24"] : cidr => index
  }
  private_subnets = {
    for index, cidr in ["10.42.10.0/24", "10.42.11.0/24"] : cidr => index
  }
  container_image = "${aws_ecr_repository.app.repository_url}:${var.image_tag}"
  remediation_cluster_name = coalesce(
    var.ecs_remediation_cluster_name,
    var.app_name,
  )
  remediation_service_name = coalesce(
    var.ecs_remediation_service_name,
    var.app_name,
  )
  remediation_cluster_resource = "arn:${data.aws_partition.current.partition}:ecs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:cluster/${split("/", local.remediation_cluster_name)[length(split("/", local.remediation_cluster_name)) - 1]}"
  remediation_service_resource = "arn:${data.aws_partition.current.partition}:ecs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:service/${split("/", local.remediation_cluster_name)[length(split("/", local.remediation_cluster_name)) - 1]}/${local.remediation_service_name}"
  common_tags = {
    Project = var.app_name
  }
}

resource "aws_ecr_repository" "app" {
  name                 = var.app_name
  image_tag_mutability = "IMMUTABLE"
  force_delete         = false

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }
}

resource "aws_ecr_lifecycle_policy" "app" {
  repository = aws_ecr_repository.app.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Expire untagged images older than seven days"
      selection = {
        tagStatus   = "untagged"
        countType   = "sinceImagePushed"
        countUnit   = "days"
        countNumber = 7
      }
      action = {
        type = "expire"
      }
    }]
  })
}

resource "aws_vpc" "app" {
  cidr_block           = "10.42.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(local.common_tags, { Name = "${var.app_name}-vpc" })
}

resource "aws_internet_gateway" "app" {
  vpc_id = aws_vpc.app.id

  tags = merge(local.common_tags, { Name = "${var.app_name}-igw" })
}

resource "aws_subnet" "public" {
  for_each = local.public_subnets

  vpc_id                  = aws_vpc.app.id
  cidr_block              = each.key
  availability_zone       = local.availability_zones[each.value]
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, { Name = "${var.app_name}-public-${each.value}" })
}

resource "aws_subnet" "private" {
  for_each = local.private_subnets

  vpc_id            = aws_vpc.app.id
  cidr_block        = each.key
  availability_zone = local.availability_zones[each.value]

  tags = merge(local.common_tags, { Name = "${var.app_name}-private-${each.value}" })
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.app.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.app.id
  }

  tags = merge(local.common_tags, { Name = "${var.app_name}-public" })
}

resource "aws_route_table_association" "public" {
  for_each = aws_subnet.public

  subnet_id      = each.value.id
  route_table_id = aws_route_table.public.id
}

resource "aws_eip" "nat" {
  domain = "vpc"

  tags = merge(local.common_tags, { Name = "${var.app_name}-nat" })
}

resource "aws_nat_gateway" "app" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public["10.42.0.0/24"].id

  depends_on = [aws_internet_gateway.app]
  tags       = merge(local.common_tags, { Name = "${var.app_name}-nat" })
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.app.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.app.id
  }

  tags = merge(local.common_tags, { Name = "${var.app_name}-private" })
}

resource "aws_route_table_association" "private" {
  for_each = aws_subnet.private

  subnet_id      = each.value.id
  route_table_id = aws_route_table.private.id
}

resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${var.app_name}"
  retention_in_days = var.log_retention_days

  tags = local.common_tags
}

resource "aws_cloudwatch_log_group" "vpc_flow" {
  name              = "/vpc/${var.app_name}/flow"
  retention_in_days = var.log_retention_days

  tags = local.common_tags
}

resource "aws_dynamodb_table" "remediation_requests" {
  name         = "${var.app_name}-remediation-requests"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "request_id"

  attribute {
    name = "request_id"
    type = "S"
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }

  server_side_encryption {
    enabled = true
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = local.common_tags
}

resource "aws_cognito_user_pool" "app" {
  name                     = "${var.app_name}-users"
  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  admin_create_user_config {
    allow_admin_create_user_only = true
  }

  password_policy {
    minimum_length                   = 12
    require_lowercase                = true
    require_numbers                  = true
    require_symbols                  = true
    require_uppercase                = true
    temporary_password_validity_days = 7
  }

  tags = local.common_tags
}

resource "aws_cognito_user_pool_domain" "app" {
  domain       = var.cognito_domain_prefix
  user_pool_id = aws_cognito_user_pool.app.id
}

resource "aws_cognito_user_pool_client" "app" {
  name                                 = "${var.app_name}-web"
  user_pool_id                         = aws_cognito_user_pool.app.id
  generate_secret                      = false
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["openid", "email"]
  supported_identity_providers         = ["COGNITO"]
  callback_urls                        = ["https://${var.application_domain_name}/"]
  logout_urls                          = ["https://${var.application_domain_name}/"]
  enable_token_revocation              = true
  prevent_user_existence_errors        = "ENABLED"

  token_validity_units {
    id_token = "minutes"
  }

  id_token_validity = 60
}

resource "aws_cognito_user_group" "approvers" {
  name         = "IncidentApprovers"
  description  = "Users permitted to approve predefined ECS remediation actions."
  user_pool_id = aws_cognito_user_pool.app.id
}

data "aws_iam_policy_document" "flow_logs_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["vpc-flow-logs.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "flow_logs" {
  name               = "${var.app_name}-flow-logs"
  assume_role_policy = data.aws_iam_policy_document.flow_logs_assume_role.json
}

data "aws_iam_policy_document" "flow_logs" {
  statement {
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["${aws_cloudwatch_log_group.vpc_flow.arn}:*"]
  }

  statement {
    actions   = ["logs:DescribeLogGroups", "logs:DescribeLogStreams"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "flow_logs" {
  name   = "${var.app_name}-flow-logs"
  role   = aws_iam_role.flow_logs.id
  policy = data.aws_iam_policy_document.flow_logs.json
}

resource "aws_flow_log" "app" {
  vpc_id               = aws_vpc.app.id
  traffic_type         = "ALL"
  log_destination_type = "cloud-watch-logs"
  log_destination      = aws_cloudwatch_log_group.vpc_flow.arn
  iam_role_arn         = aws_iam_role.flow_logs.arn

  depends_on = [aws_iam_role_policy.flow_logs]
}

resource "aws_security_group" "alb" {
  name        = "${var.app_name}-alb"
  description = "HTTPS ingress from approved clients; egress only to the ECS tasks."
  vpc_id      = aws_vpc.app.id

  tags = merge(local.common_tags, { Name = "${var.app_name}-alb" })
}

resource "aws_security_group" "tasks" {
  name        = "${var.app_name}-tasks"
  description = "Only the ALB may reach the application containers."
  vpc_id      = aws_vpc.app.id

  tags = merge(local.common_tags, { Name = "${var.app_name}-tasks" })
}

resource "aws_vpc_security_group_ingress_rule" "alb" {
  for_each = toset(var.allowed_client_cidrs)

  security_group_id = aws_security_group.alb.id
  cidr_ipv4         = each.value
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80

  description = "HTTP redirect from approved clients"
}

resource "aws_vpc_security_group_ingress_rule" "alb_https" {
  for_each = toset(var.allowed_client_cidrs)

  security_group_id = aws_security_group.alb.id
  cidr_ipv4         = each.value
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443

  description = "HTTPS from approved clients"
}

resource "aws_vpc_security_group_egress_rule" "alb_ui" {
  security_group_id            = aws_security_group.alb.id
  referenced_security_group_id = aws_security_group.tasks.id
  ip_protocol                  = "tcp"
  from_port                    = 8501
  to_port                      = 8501
  description                  = "Streamlit target"
}

resource "aws_vpc_security_group_egress_rule" "alb_api" {
  security_group_id            = aws_security_group.alb.id
  referenced_security_group_id = aws_security_group.tasks.id
  ip_protocol                  = "tcp"
  from_port                    = 8000
  to_port                      = 8000
  description                  = "FastAPI target"
}

resource "aws_vpc_security_group_ingress_rule" "tasks_ui" {
  security_group_id            = aws_security_group.tasks.id
  referenced_security_group_id = aws_security_group.alb.id
  ip_protocol                  = "tcp"
  from_port                    = 8501
  to_port                      = 8501
  description                  = "Streamlit from ALB"
}

resource "aws_vpc_security_group_ingress_rule" "tasks_api" {
  security_group_id            = aws_security_group.tasks.id
  referenced_security_group_id = aws_security_group.alb.id
  ip_protocol                  = "tcp"
  from_port                    = 8000
  to_port                      = 8000
  description                  = "FastAPI from ALB"
}

resource "aws_vpc_security_group_egress_rule" "tasks_https" {
  security_group_id = aws_security_group.tasks.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  description       = "HTTPS egress for Groq and AWS APIs"
}

resource "aws_lb" "app" {
  name                       = substr("${var.app_name}-alb", 0, 32)
  internal                   = false
  load_balancer_type         = "application"
  security_groups            = [aws_security_group.alb.id]
  subnets                    = [for subnet in aws_subnet.public : subnet.id]
  idle_timeout               = 300
  enable_deletion_protection = true

  tags = local.common_tags
}

resource "aws_route53_record" "app" {
  count = var.route53_zone_id == null ? 0 : 1

  zone_id = var.route53_zone_id
  name    = var.application_domain_name
  type    = "A"

  alias {
    name                   = aws_lb.app.dns_name
    zone_id                = aws_lb.app.zone_id
    evaluate_target_health = true
  }
}

resource "aws_lb_target_group" "ui" {
  name        = substr("${var.app_name}-ui", 0, 32)
  port        = 8501
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = aws_vpc.app.id

  health_check {
    enabled             = true
    path                = "/_stcore/health"
    matcher             = "200-399"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }

  tags = local.common_tags
}

resource "aws_lb_target_group" "api" {
  name        = substr("${var.app_name}-api", 0, 32)
  port        = 8000
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = aws_vpc.app.id

  health_check {
    enabled             = true
    path                = "/health"
    matcher             = "200-399"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }

  tags = local.common_tags
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.app.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ui.arn
  }
}

resource "aws_lb_listener_rule" "api" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 10

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }

  condition {
    path_pattern {
      values = [
        "/incident",
        "/health",
        "/docs*",
        "/openapi.json",
        "/redoc*",
        "/remediation-requests*",
      ]
    }
  }
}

data "aws_iam_policy_document" "ecs_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "execution" {
  name               = "${var.app_name}-execution"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role.json
}

resource "aws_iam_role" "task" {
  name               = "${var.app_name}-task"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role.json
}

data "aws_iam_policy_document" "execution" {
  statement {
    sid       = "GetEcrAuthorizationToken"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }

  statement {
    sid = "PullApplicationImage"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
    ]
    resources = [aws_ecr_repository.app.arn]
  }

  statement {
    sid       = "WriteContainerLogs"
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["${aws_cloudwatch_log_group.app.arn}:*"]
  }

  statement {
    sid       = "ReadGroqSecret"
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [var.groq_secret_arn]
  }

  dynamic "statement" {
    for_each = var.groq_kms_key_arn == null ? [] : [var.groq_kms_key_arn]

    content {
      sid       = "DecryptGroqSecret"
      actions   = ["kms:Decrypt"]
      resources = [statement.value]
    }
  }
}

resource "aws_iam_role_policy" "execution" {
  name   = "${var.app_name}-execution"
  role   = aws_iam_role.execution.id
  policy = data.aws_iam_policy_document.execution.json
}

data "aws_iam_policy_document" "task_remediation" {
  statement {
    sid       = "InspectConfiguredEcsService"
    actions   = ["ecs:DescribeServices"]
    resources = [local.remediation_cluster_resource, local.remediation_service_resource]
  }

  statement {
    sid       = "ListTaskDefinitionRevisions"
    actions   = ["ecs:ListTaskDefinitions"]
    resources = ["*"]
  }

  statement {
    sid       = "UpdateOnlyConfiguredEcsService"
    actions   = ["ecs:UpdateService"]
    resources = [local.remediation_service_resource]
  }

  statement {
    sid = "AuditPendingRemediationRequests"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:Scan",
      "dynamodb:UpdateItem",
    ]
    resources = [aws_dynamodb_table.remediation_requests.arn]
  }
}

resource "aws_iam_role_policy" "task_remediation" {
  name   = "${var.app_name}-approved-remediation"
  role   = aws_iam_role.task.id
  policy = data.aws_iam_policy_document.task_remediation.json
}

resource "aws_ecs_cluster" "app" {
  name = var.app_name
  tags = local.common_tags
}

resource "aws_ecs_task_definition" "app" {
  family                   = var.app_name
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 2048
  memory                   = 4096
  execution_role_arn       = aws_iam_role.execution.arn
  task_role_arn            = aws_iam_role.task.arn

  container_definitions = jsonencode([
    {
      name      = "incident-api"
      image     = local.container_image
      essential = true
      portMappings = [{
        containerPort = 8000
        protocol      = "tcp"
      }]
      environment = [
        { name = "MODEL_NAME", value = "llama-3.3-70b-versatile" },
        { name = "LOG_LEVEL", value = "INFO" },
        { name = "AWS_REGION", value = var.aws_region },
        { name = "ECS_CLUSTER_NAME", value = local.remediation_cluster_name },
        { name = "ECS_SERVICE_NAME", value = local.remediation_service_name },
        { name = "REMEDIATION_TABLE_NAME", value = aws_dynamodb_table.remediation_requests.name },
        { name = "COGNITO_USER_POOL_ID", value = aws_cognito_user_pool.app.id },
        { name = "COGNITO_APP_CLIENT_ID", value = aws_cognito_user_pool_client.app.id },
        { name = "COGNITO_ISSUER_URL", value = "https://cognito-idp.${var.aws_region}.amazonaws.com/${aws_cognito_user_pool.app.id}" },
        { name = "COGNITO_APPROVER_GROUP", value = aws_cognito_user_group.approvers.name },
        { name = "COGNITO_HOSTED_UI_DOMAIN", value = "https://${aws_cognito_user_pool_domain.app.domain}.auth.${var.aws_region}.amazoncognito.com" },
        { name = "APP_PUBLIC_URL", value = "https://${var.application_domain_name}" },
      ]
      secrets = [{
        name      = "GROQ_API_KEY"
        valueFrom = var.groq_secret_arn
      }]
      healthCheck = {
        command = [
          "CMD-SHELL",
          "python -c \"import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5).read()\" || exit 1",
        ]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 180
      }
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.app.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "api"
        }
      }
    },
    {
      name      = "incident-ui"
      image     = local.container_image
      essential = true
      command   = ["streamlit", "run", "ui/streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]
      portMappings = [{
        containerPort = 8501
        protocol      = "tcp"
      }]
      environment = [{
        name  = "API_BASE_URL"
        value = "http://127.0.0.1:8000"
        }, {
        name  = "COGNITO_APP_CLIENT_ID"
        value = aws_cognito_user_pool_client.app.id
        }, {
        name  = "COGNITO_HOSTED_UI_DOMAIN"
        value = "https://${aws_cognito_user_pool_domain.app.domain}.auth.${var.aws_region}.amazoncognito.com"
        }, {
        name  = "APP_PUBLIC_URL"
        value = "https://${var.application_domain_name}"
      }]
      dependsOn = [{
        containerName = "incident-api"
        condition     = "HEALTHY"
      }]
      healthCheck = {
        command = [
          "CMD-SHELL",
          "python -c \"import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=5).read()\" || exit 1",
        ]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.app.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ui"
        }
      }
    },
  ])

  tags = local.common_tags
}

resource "aws_ecs_service" "app" {
  name                               = var.app_name
  cluster                            = aws_ecs_cluster.app.id
  task_definition                    = aws_ecs_task_definition.app.arn
  desired_count                      = 1
  launch_type                        = "FARGATE"
  platform_version                   = "LATEST"
  health_check_grace_period_seconds  = 180
  enable_execute_command             = false
  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 100

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  lifecycle {
    precondition {
      condition = (
        (var.ecs_remediation_cluster_name == null)
        == (var.ecs_remediation_service_name == null)
      )
      error_message = "Set both ecs_remediation_cluster_name and ecs_remediation_service_name, or leave both unset."
    }
  }

  network_configuration {
    subnets          = [for subnet in aws_subnet.private : subnet.id]
    security_groups  = [aws_security_group.tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "incident-api"
    container_port   = 8000
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.ui.arn
    container_name   = "incident-ui"
    container_port   = 8501
  }

  depends_on = [
    aws_lb_listener.https,
    aws_lb_listener_rule.api,
    aws_iam_role_policy.execution,
    aws_iam_role_policy.task_remediation,
  ]

  tags = local.common_tags
}

resource "aws_budgets_budget" "monthly" {
  count = var.budget_alert_email == null ? 0 : 1

  name         = "${var.app_name}-monthly-cost"
  budget_type  = "COST"
  limit_amount = tostring(var.monthly_budget_usd)
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.budget_alert_email]
  }

  tags = local.common_tags
}

resource "aws_sns_topic" "alarms" {
  count = var.alarm_email == null ? 0 : 1

  name = "${var.app_name}-alarms"
  tags = local.common_tags
}

resource "aws_sns_topic_subscription" "alarm_email" {
  count = var.alarm_email == null ? 0 : 1

  topic_arn = aws_sns_topic.alarms[0].arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

resource "aws_cloudwatch_metric_alarm" "ecs_cpu" {
  alarm_name          = "${var.app_name}-ecs-cpu-high"
  alarm_description   = "ECS service CPU utilization exceeded 80% for 10 minutes."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  treat_missing_data  = "notBreaching"
  alarm_actions       = var.alarm_email == null ? [] : [aws_sns_topic.alarms[0].arn]
  ok_actions          = var.alarm_email == null ? [] : [aws_sns_topic.alarms[0].arn]

  dimensions = {
    ClusterName = aws_ecs_cluster.app.name
    ServiceName = aws_ecs_service.app.name
  }
}

resource "aws_cloudwatch_metric_alarm" "ecs_memory" {
  alarm_name          = "${var.app_name}-ecs-memory-high"
  alarm_description   = "ECS service memory utilization exceeded 85% for 10 minutes."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 85
  treat_missing_data  = "notBreaching"
  alarm_actions       = var.alarm_email == null ? [] : [aws_sns_topic.alarms[0].arn]
  ok_actions          = var.alarm_email == null ? [] : [aws_sns_topic.alarms[0].arn]

  dimensions = {
    ClusterName = aws_ecs_cluster.app.name
    ServiceName = aws_ecs_service.app.name
  }
}

resource "aws_cloudwatch_metric_alarm" "alb_unhealthy_targets" {
  alarm_name          = "${var.app_name}-alb-unhealthy-targets"
  alarm_description   = "At least one application target is unhealthy."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "UnHealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Maximum"
  threshold           = 1
  treat_missing_data  = "notBreaching"
  alarm_actions       = var.alarm_email == null ? [] : [aws_sns_topic.alarms[0].arn]
  ok_actions          = var.alarm_email == null ? [] : [aws_sns_topic.alarms[0].arn]

  dimensions = {
    LoadBalancer = aws_lb.app.arn_suffix
    TargetGroup  = aws_lb_target_group.api.arn_suffix
  }
}

resource "aws_cloudwatch_metric_alarm" "alb_elb_5xx" {
  alarm_name          = "${var.app_name}-alb-5xx-errors"
  alarm_description   = "The ALB generated at least five 5xx errors in a five-minute period."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "HTTPCode_ELB_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  treat_missing_data  = "notBreaching"
  alarm_actions       = var.alarm_email == null ? [] : [aws_sns_topic.alarms[0].arn]
  ok_actions          = var.alarm_email == null ? [] : [aws_sns_topic.alarms[0].arn]

  dimensions = {
    LoadBalancer = aws_lb.app.arn_suffix
  }
}

resource "aws_cloudwatch_dashboard" "app" {
  dashboard_name = var.app_name

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "ECS service utilization"
          view   = "timeSeries"
          region = var.aws_region
          period = 300
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ClusterName", aws_ecs_cluster.app.name, "ServiceName", aws_ecs_service.app.name],
            [".", "MemoryUtilization", ".", ".", ".", "."],
          ]
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "ALB requests, latency, and target health"
          view   = "timeSeries"
          region = var.aws_region
          period = 300
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", aws_lb.app.arn_suffix, { stat = "Sum" }],
            [".", "TargetResponseTime", ".", ".", { stat = "Average", yAxis = "right" }],
            [".", "UnHealthyHostCount", ".", ".", "TargetGroup", aws_lb_target_group.api.arn_suffix, { stat = "Maximum", yAxis = "right" }],
          ]
        }
      },
      {
        type   = "alarm"
        x      = 0
        y      = 6
        width  = 24
        height = 6
        properties = {
          title = "Application alarms"
          alarms = [
            aws_cloudwatch_metric_alarm.ecs_cpu.arn,
            aws_cloudwatch_metric_alarm.ecs_memory.arn,
            aws_cloudwatch_metric_alarm.alb_unhealthy_targets.arn,
            aws_cloudwatch_metric_alarm.alb_elb_5xx.arn,
          ]
        }
      },
    ]
  })
}
