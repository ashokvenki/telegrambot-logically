provider "aws" {
  region = var.aws_region
}

# -------------------------
# Locals (naming + tagging)
# -------------------------
locals {
  project = "telegram-bot"

  tags = {
    Project     = local.project
    Environment = var.environment
    Owner       = "CloudBots"
  }
}

# -------------------------
# DynamoDB Module
# -------------------------
module "dynamodb" {
  source     = "./modules/dynamodb"
  table_name = var.dynamo_table
  tags       = local.tags
}

# -------------------------
# S3 Module
# -------------------------
module "s3" {
  source      = "./modules/s3"
  bucket_name = var.s3_bucket
  tags        = local.tags
}

# -------------------------
# IAM Module (Least Privilege)
# -------------------------
module "iam" {
  source         = "./modules/iam"
  dynamo_arn     = module.dynamodb.table_arn
  s3_bucket_arn = module.s3.bucket_arn
  tags           = local.tags
}

# -------------------------
# Lambda Module
# -------------------------
module "lambda" {
  source         = "./modules/lambda"
  function_name = var.lambda_function_name
  role_arn      = module.iam.lambda_role_arn
  dynamo_table  = module.dynamodb.table_name
  s3_bucket     = module.s3.bucket_name
  telegram_token = var.telegram_token
  tags          = local.tags
}

# -------------------------
# API Gateway Module
# -------------------------
module "api_gateway" {
  source       = "./modules/api_gateway"
  lambda_arn   = module.lambda.lambda_arn
  lambda_name  = module.lambda.lambda_name
  stage_name   = var.environment
  tags         = local.tags
}
