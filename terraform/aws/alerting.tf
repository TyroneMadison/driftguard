# Delivery rail for drift findings and health alarms.

resource "aws_sns_topic" "drift_alerts" {
  name = "${var.name_prefix}-alerts"
}

resource "aws_sns_topic_subscription" "email" {
  count = var.alert_email == "" ? 0 : 1

  topic_arn = aws_sns_topic.drift_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# The scanner publishes custom metrics after every scheduled run:
#   aws cloudwatch put-metric-data --namespace DriftGuard \
#     --metric-name CriticalDrift --value <count> --dimensions Stack=aws-prod
resource "aws_cloudwatch_metric_alarm" "critical_drift" {
  alarm_name          = "${var.name_prefix}-critical-drift"
  alarm_description   = "One or more critical drift findings on the last scan"
  namespace           = "DriftGuard"
  metric_name         = "CriticalDrift"
  statistic           = "Maximum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"
  treat_missing_data  = "notBreaching"

  alarm_actions = [aws_sns_topic.drift_alerts.arn]
  ok_actions    = [aws_sns_topic.drift_alerts.arn]
}

# Anomaly detection on total drift volume: a sudden spike in drift count
# usually means an unreviewed change wave or automation misfiring.
resource "aws_cloudwatch_metric_alarm" "drift_volume_anomaly" {
  alarm_name          = "${var.name_prefix}-drift-volume-anomaly"
  alarm_description   = "Drift volume outside the expected band"
  comparison_operator = "GreaterThanUpperThreshold"
  evaluation_periods  = 2
  threshold_metric_id = "band"
  treat_missing_data  = "notBreaching"

  metric_query {
    id          = "band"
    expression  = "ANOMALY_DETECTION_BAND(drift, 2)"
    label       = "Expected drift volume"
    return_data = true
  }

  metric_query {
    id          = "drift"
    return_data = true

    metric {
      namespace   = "DriftGuard"
      metric_name = "DriftCount"
      period      = 3600
      stat        = "Sum"
    }
  }

  alarm_actions = [aws_sns_topic.drift_alerts.arn]
}
