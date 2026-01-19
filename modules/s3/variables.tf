variable "bucket_name" {
  type        = string
  description = "Name of the S3 bucket for user files"
}

variable "tags" {
  type        = map(string)
  description = "Common resource tags"
}
