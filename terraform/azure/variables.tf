variable "location" {
  description = "Azure region"
  type        = string
  default     = "eastus"
}

variable "name_prefix" {
  description = "Prefix for all DriftGuard resources"
  type        = string
  default     = "driftguard"
}

variable "alert_email" {
  description = "Optional email receiver for the action group"
  type        = string
  default     = ""
}
