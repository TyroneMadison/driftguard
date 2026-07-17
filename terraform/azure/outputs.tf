output "action_group_id" {
  description = "Action group receiving drift and health alerts"
  value       = azurerm_monitor_action_group.drift_alerts.id
}

output "demo_storage_account" {
  description = "Monitored demo storage account"
  value       = azurerm_storage_account.logs.name
}
