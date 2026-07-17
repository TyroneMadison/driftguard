output "alert_topic_arn" {
  description = "SNS topic receiving drift and anomaly alerts"
  value       = aws_sns_topic.drift_alerts.arn
}

output "demo_bucket" {
  description = "Monitored demo bucket"
  value       = aws_s3_bucket.artifacts.bucket
}
