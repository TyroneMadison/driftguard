# Tiny demo stack that scheduled scans watch. Flip a tag or a parameter
# in the console and the next scan reports it.

resource "aws_s3_bucket" "artifacts" {
  bucket_prefix = "${var.name_prefix}-artifacts-"
  force_destroy = true

  tags = {
    environment = "demo"
    owner       = "platform"
  }
}

resource "aws_s3_bucket_versioning" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_ssm_parameter" "feature_flag" {
  name  = "/${var.name_prefix}-demo/feature-flag"
  type  = "String"
  value = "enabled"

  tags = {
    environment = "demo"
  }
}
