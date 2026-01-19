output "lambda_arn" {
  value       = aws_lambda_function.this.arn
  description = "Lambda function ARN"
}

output "lambda_name" {
  value       = aws_lambda_function.this.function_name
  description = "Lambda function name"
}
