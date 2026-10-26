output "application_url" {
  description = "HTTPS URL for the Streamlit application."
  value       = "https://${var.application_domain_name}"
}

output "load_balancer_dns_name" {
  description = "ALB DNS name. Point application_domain_name to this if Route 53 is not configured."
  value       = aws_lb.app.dns_name
}

output "ecr_repository_url" {
  description = "ECR repository URL for publishing the application image."
  value       = aws_ecr_repository.app.repository_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name."
  value       = aws_ecs_cluster.app.name
}

output "ecs_service_name" {
  description = "ECS service name."
  value       = aws_ecs_service.app.name
}

output "cloudwatch_dashboard_name" {
  description = "CloudWatch dashboard name for service and ALB metrics."
  value       = aws_cloudwatch_dashboard.app.dashboard_name
}

output "cloudwatch_alarm_topic_arn" {
  description = "SNS topic ARN for application alarms, or null if alarm_email is not configured."
  value       = var.alarm_email == null ? null : aws_sns_topic.alarms[0].arn
}

output "cognito_user_pool_id" {
  description = "Cognito user pool ID for application sign-in."
  value       = aws_cognito_user_pool.app.id
}

output "cognito_app_client_id" {
  description = "Public Cognito app client ID used by the Streamlit UI."
  value       = aws_cognito_user_pool_client.app.id
}

output "cognito_hosted_ui_domain" {
  description = "Cognito hosted UI domain used for sign-in."
  value       = "https://${aws_cognito_user_pool_domain.app.domain}.auth.${var.aws_region}.amazoncognito.com"
}

output "remediation_target" {
  description = "The single ECS cluster/service permitted for approved remediation."
  value       = "${local.remediation_cluster_name}/${local.remediation_service_name}"
}
