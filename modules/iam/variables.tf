variable "dynamo_arn" {
  type        = string
  description = "ARN of the DynamoDB table"
}

variable "s3_bucket_arn" {
  type        = string
  description = "ARN of the S3 bucket"
}

variable "tags" {
  type        = map(string)
  description = "Common resource tags"
}
