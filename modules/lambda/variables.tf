variable "function_name" {
  type        = string
  description = "Lambda function name"
}

variable "role_arn" {
  type        = string
  description = "IAM role ARN for Lambda execution"
}

variable "dynamo_table" {
  type        = string
  description = "DynamoDB table name"
}

variable "s3_bucket" {
  type        = string
  description = "S3 bucket name for user files"
}

variable "tags" {
  type        = map(string)
  description = "Common resource tags"
}

variable "telegram_token" {
  type        = string
  description = "Telegram bot token"
  sensitive   = true
}
