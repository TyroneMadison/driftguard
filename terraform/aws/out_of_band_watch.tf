# Real-time tripwire: security-relevant API calls made outside pipelines
# raise an event immediately, without waiting for the next scheduled scan.
# Requires CloudTrail enabled in the account.

resource "aws_cloudwatch_event_rule" "security_group_writes" {
  name        = "${var.name_prefix}-sg-writes"
  description = "Out-of-band security group modifications"

  event_pattern = jsonencode({
    source      = ["aws.ec2"]
    detail-type = ["AWS API Call via CloudTrail"]
    detail = {
      eventName = [
        "AuthorizeSecurityGroupIngress",
        "AuthorizeSecurityGroupEgress",
        "RevokeSecurityGroupIngress",
        "RevokeSecurityGroupEgress",
        "ModifySecurityGroupRules"
      ]
    }
  })
}

resource "aws_cloudwatch_event_target" "sg_writes_to_sns" {
  rule      = aws_cloudwatch_event_rule.security_group_writes.name
  target_id = "sns"
  arn       = aws_sns_topic.drift_alerts.arn
}

resource "aws_sns_topic_policy" "allow_eventbridge" {
  arn    = aws_sns_topic.drift_alerts.arn
  policy = data.aws_iam_policy_document.allow_eventbridge.json
}

data "aws_iam_policy_document" "allow_eventbridge" {
  statement {
    sid     = "AllowEventBridgePublish"
    effect  = "Allow"
    actions = ["SNS:Publish"]

    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }

    resources = [aws_sns_topic.drift_alerts.arn]
  }
}
