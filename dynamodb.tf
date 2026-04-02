# ============================================
# DynamoDB Table
# ============================================

resource "aws_dynamodb_table" "tasks" {
  name           = "${var.project_name}-${var.environment}-tasks"
  billing_mode   = "PAY_PER_REQUEST"  # On-demand (gratis con Free Tier)
  
  # Partition key: userId
  # Sort key: taskId
  hash_key  = "userId"
  range_key = "taskId"

  # Attributes (solo las que se usan como keys)
  attribute {
    name = "userId"
    type = "S"  # String
  }

  attribute {
    name = "taskId"
    type = "S"
  }

  # Point-in-time recovery (backup continuo)
  point_in_time_recovery {
    enabled = true
  }

  # Tags
  tags = {
    Name        = "${var.project_name}-tasks-table"
    Environment = var.environment
  }
}

# ============================================
# Output
# ============================================

output "dynamodb_table_name" {
  description = "Nombre de la tabla DynamoDB"
  value       = aws_dynamodb_table.tasks.name
}

output "dynamodb_table_arn" {
  description = "ARN de la tabla DynamoDB"
  value       = aws_dynamodb_table.tasks.arn
}