resource "aws_lambda_function" "this" {
  function_name = var.function_name
  role          = var.role_arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.11"
  filename      = "lambda_function.zip"

  timeout     = 15
  memory_size = 128

  environment {
    variables = {
      DYNAMO_TABLE   = var.dynamo_table
      S3_BUCKET      = var.s3_bucket
      TELEGRAM_TOKEN = var.telegram_token
    }
  }

  tags = var.tags
}
