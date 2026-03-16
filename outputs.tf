# URL del API
output "api_url" {
  description = "URL base del API Gateway"
  value       = "${aws_api_gateway_stage.api_stage.invoke_url}/tasks"
}

# Nombre de la tabla DynamoDB
output "dynamodb_table_name" {
  description = "Nombre de la tabla DynamoDB"
  value       = aws_dynamodb_table.tasks.name
}

# ARN del IAM Role de Lambda
output "lambda_role_arn" {
  description = "ARN del IAM role de Lambda"
  value       = aws_iam_role.lambda_role.arn
}

# Nombres de las funciones Lambda
output "lambda_functions" {
  description = "Nombres de las funciones Lambda"
  value = {
    get_tasks    = aws_lambda_function.get_tasks.function_name
    create_task  = aws_lambda_function.create_task.function_name
    update_task  = aws_lambda_function.update_task.function_name
  }
}