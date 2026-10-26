variable "app_name" {
  description = "Prefix used to name resources."
  type        = string
  default     = "incident-resolution"
}

variable "aws_region" {
  description = "AWS region for all regional resources. The ACM certificate must be in this region."
  type        = string
  default     = "ap-south-1"
}

variable "image_tag" {
  description = "Immutable tag of the application image already pushed to ECR."
  type        = string
  default     = "v1"
}

variable "groq_secret_arn" {
  description = "ARN of an existing Secrets Manager secret containing the Groq API key."
  type        = string
  sensitive   = true
}

variable "groq_kms_key_arn" {
  description = "Optional customer-managed KMS key ARN used to encrypt the Groq secret."
  type        = string
  default     = null
}

variable "certificate_arn" {
  description = "ARN of an issued ACM certificate in aws_region for the ALB HTTPS listener."
  type        = string
}

variable "application_domain_name" {
  description = "DNS name covered by the ACM certificate and used to reach the application."
  type        = string
}

variable "cognito_domain_prefix" {
  description = "Globally unique Cognito hosted UI domain prefix for sign-in."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$", var.cognito_domain_prefix))
    error_message = "Use a 1-63 character lowercase Cognito prefix containing only letters, numbers, and interior hyphens."
  }
}

variable "ecs_remediation_cluster_name" {
  description = "Optional ECS cluster name for the single human-remediation target. Defaults to this application's cluster."
  type        = string
  default     = null
}

variable "ecs_remediation_service_name" {
  description = "Optional ECS service name for the single human-remediation target. Defaults to this application's service."
  type        = string
  default     = null
}

variable "route53_zone_id" {
  description = "Optional Route 53 hosted-zone ID in which to create an ALB alias record."
  type        = string
  default     = null
}

variable "allowed_client_cidrs" {
  description = "CIDR blocks allowed to reach the HTTPS load balancer. Restrict this to trusted client ranges where possible."
  type        = list(string)

  validation {
    condition     = length(var.allowed_client_cidrs) > 0
    error_message = "Provide at least one trusted client CIDR; use 0.0.0.0/0 only when the application must be public."
  }
}

variable "log_retention_days" {
  description = "Retention period for application and VPC flow logs."
  type        = number
  default     = 30
}

variable "budget_alert_email" {
  description = "Optional email address for a monthly AWS cost alert at 80% of the budget."
  type        = string
  default     = null
}

variable "alarm_email" {
  description = "Optional email address for CloudWatch application alarm notifications."
  type        = string
  default     = null
}

variable "monthly_budget_usd" {
  description = "Monthly AWS cost alert threshold in USD, used when budget_alert_email is set."
  type        = number
  default     = 100
}
