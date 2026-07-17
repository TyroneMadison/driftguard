resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "azurerm_resource_group" "this" {
  name     = "rg-${var.name_prefix}"
  location = var.location

  tags = {
    project    = "driftguard"
    managed_by = "terraform"
  }
}

# Delivery rail for drift findings and platform alerts.
resource "azurerm_monitor_action_group" "drift_alerts" {
  name                = "ag-${var.name_prefix}"
  resource_group_name = azurerm_resource_group.this.name
  short_name          = "driftgrd"

  dynamic "email_receiver" {
    for_each = var.alert_email == "" ? [] : [var.alert_email]

    content {
      name          = "oncall"
      email_address = email_receiver.value
    }
  }
}

# Monitored demo resource: flip a tag in the portal, the next scan sees it.
resource "azurerm_storage_account" "logs" {
  name                     = "st${var.name_prefix}${random_string.suffix.result}"
  resource_group_name      = azurerm_resource_group.this.name
  location                 = azurerm_resource_group.this.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"

  tags = {
    environment = "demo"
    owner       = "platform"
  }
}

# Health signal: storage availability dips page immediately.
resource "azurerm_monitor_metric_alert" "storage_availability" {
  name                = "alert-${var.name_prefix}-storage-availability"
  resource_group_name = azurerm_resource_group.this.name
  scopes              = [azurerm_storage_account.logs.id]
  description         = "Storage availability below 100 percent"
  severity            = 1
  frequency           = "PT5M"
  window_size         = "PT15M"

  criteria {
    metric_namespace = "Microsoft.Storage/storageAccounts"
    metric_name      = "Availability"
    aggregation      = "Average"
    operator         = "LessThan"
    threshold        = 100
  }

  action {
    action_group_id = azurerm_monitor_action_group.drift_alerts.id
  }
}

# Real-time tripwire: NSG writes outside pipelines raise an activity log
# alert immediately, without waiting for the next scheduled scan.
resource "azurerm_monitor_activity_log_alert" "nsg_writes" {
  name                = "alert-${var.name_prefix}-nsg-writes"
  resource_group_name = azurerm_resource_group.this.name
  location            = "global"
  scopes              = [azurerm_resource_group.this.id]
  description         = "Out-of-band network security group modifications"

  criteria {
    category       = "Administrative"
    operation_name = "Microsoft.Network/networkSecurityGroups/write"
  }

  action {
    action_group_id = azurerm_monitor_action_group.drift_alerts.id
  }
}
