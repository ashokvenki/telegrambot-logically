variable "lambda_arn" {
  type        = string
  description = "Lambda function ARN to invoke"
}

variable "lambda_name" {
  type        = string
  description = "Lambda function name"
}

variable "stage_name" {
  type        = string
  default     = "prod"
}

variable "tags" {
  type        = map(string)
  description = "Common resource tags"
}
