resource "aws_dynamodb_table" "this" {
  name         = var.table_name
  billing_mode = "PAY_PER_REQUEST"

  hash_key  = "user_id"
  range_key = "note_id"

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "note_id"
    type = "S"
  }

  tags = var.tags
}
