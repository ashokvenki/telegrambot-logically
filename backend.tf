terraform {
  backend "s3" {
    bucket  = "cloudbots-terraform-state"
    key     = "telegram-bot/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}

