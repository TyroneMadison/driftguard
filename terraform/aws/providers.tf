provider "aws" {
  region = var.region

  default_tags {
    tags = {
      project    = "driftguard"
      managed_by = "terraform"
    }
  }
}
