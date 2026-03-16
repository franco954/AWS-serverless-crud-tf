
resource "aws_dynamodb_table" "tasks" {
 
  name = "${var.project_name}-${var.environment}-tasks"
  
  # Modo de billing
  billing_mode = "PAY_PER_REQUEST"
  
  # Partition key - identificador único de cada item
  hash_key = "taskId"
  
  attribute {
    name = "taskId"
    type = "S"  
  }
  
  tags = {
    Name = "Tasks Table"
  }
}