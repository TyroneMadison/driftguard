variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "name_prefix" {
  description = "Prefix for all DriftGuard resources"
  type        = string
  default     = "driftguard"
}

variable "alert_email" {
  description = "Optional email endpoint for the alert topic"
  type        = string
  default     = ""
}
