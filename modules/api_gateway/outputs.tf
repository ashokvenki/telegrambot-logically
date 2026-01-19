output "invoke_url" {
  value       = "https://${aws_api_gateway_rest_api.this.id}.execute-api.${data.aws_region.current.name}.amazonaws.com/${aws_api_gateway_stage.this.stage_name}/webhook"
  description = "Telegram webhook URL"
}
