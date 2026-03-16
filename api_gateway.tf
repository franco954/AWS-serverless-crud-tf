# ============================================
# API Gateway REST API
# ============================================

# Recurso principal del API
resource "aws_api_gateway_rest_api" "tasks_api" {
  name        = "${var.project_name}-${var.environment}-api"
  description = "REST API para gestión de tareas"
  
  # Configuración de endpoints
  endpoint_configuration {
    types = ["REGIONAL"]  # REGIONAL, EDGE, PRIVATE
  }
}

# ============================================
# Resource: /tasks
# ============================================

# Un "resource" en API Gateway es un path en tu URL
# Esto crea: https://abc123.execute-api.us-east-1.amazonaws.com/dev/tasks
resource "aws_api_gateway_resource" "tasks" {
  rest_api_id = aws_api_gateway_rest_api.tasks_api.id
  parent_id   = aws_api_gateway_rest_api.tasks_api.root_resource_id
  path_part   = "tasks"  # El path final
}

# ============================================
# Método: GET /tasks
# ============================================

# Define el método HTTP
resource "aws_api_gateway_method" "get_tasks" {
  rest_api_id   = aws_api_gateway_rest_api.tasks_api.id
  resource_id   = aws_api_gateway_resource.tasks.id
  http_method   = "GET"
  authorization = "NONE"  # Sin autenticación (por ahora)
  
  # Configuración de request
  request_parameters = {
    "method.request.header.Content-Type" = false
  }
}

# Integración con Lambda
resource "aws_api_gateway_integration" "get_tasks_integration" {
  rest_api_id = aws_api_gateway_rest_api.tasks_api.id
  resource_id = aws_api_gateway_resource.tasks.id
  http_method = aws_api_gateway_method.get_tasks.http_method
  
  # Tipo de integración
  integration_http_method = "POST"  # SIEMPRE POST para Lambda
  type                    = "AWS_PROXY"  # Lambda Proxy Integration
  uri                     = aws_lambda_function.get_tasks.invoke_arn
}

# Permiso para que API Gateway invoque la Lambda
resource "aws_lambda_permission" "allow_api_gateway_get" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_tasks.function_name
  principal     = "apigateway.amazonaws.com"
  
  # ARN del API Gateway
  source_arn = "${aws_api_gateway_rest_api.tasks_api.execution_arn}/*/*"
}

# ============================================
# Método: POST /tasks
# ============================================

resource "aws_api_gateway_method" "post_tasks" {
  rest_api_id   = aws_api_gateway_rest_api.tasks_api.id
  resource_id   = aws_api_gateway_resource.tasks.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "post_tasks_integration" {
  rest_api_id             = aws_api_gateway_rest_api.tasks_api.id
  resource_id             = aws_api_gateway_resource.tasks.id
  http_method             = aws_api_gateway_method.post_tasks.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.create_task.invoke_arn
}

resource "aws_lambda_permission" "allow_api_gateway_post" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.create_task.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.tasks_api.execution_arn}/*/*"
}

# ============================================
# Resource: /tasks/{id} para PUT
# ============================================

resource "aws_api_gateway_resource" "task_by_id" {
  rest_api_id = aws_api_gateway_rest_api.tasks_api.id
  parent_id   = aws_api_gateway_resource.tasks.id
  path_part   = "{id}"  # Path parameter
}

resource "aws_api_gateway_method" "put_task" {
  rest_api_id   = aws_api_gateway_rest_api.tasks_api.id
  resource_id   = aws_api_gateway_resource.task_by_id.id
  http_method   = "PUT"
  authorization = "NONE"
  
  # El {id} se pasa como path parameter
  request_parameters = {
    "method.request.path.id" = true
  }
}

resource "aws_api_gateway_integration" "put_task_integration" {
  rest_api_id             = aws_api_gateway_rest_api.tasks_api.id
  resource_id             = aws_api_gateway_resource.task_by_id.id
  http_method             = aws_api_gateway_method.put_task.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.update_task.invoke_arn
}

resource "aws_lambda_permission" "allow_api_gateway_put" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.update_task.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.tasks_api.execution_arn}/*/*"
}

# ============================================
# Método: DELETE /tasks/{id}
# ============================================

resource "aws_api_gateway_method" "delete_task" {
  rest_api_id   = aws_api_gateway_rest_api.tasks_api.id
  resource_id   = aws_api_gateway_resource.task_by_id.id
  http_method   = "DELETE"
  authorization = "NONE"
  
  request_parameters = {
    "method.request.path.id" = true
  }
}

resource "aws_api_gateway_integration" "delete_task_integration" {
  rest_api_id             = aws_api_gateway_rest_api.tasks_api.id
  resource_id             = aws_api_gateway_resource.task_by_id.id
  http_method             = aws_api_gateway_method.delete_task.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.delete_task.invoke_arn
}

resource "aws_lambda_permission" "allow_api_gateway_delete" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.delete_task.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.tasks_api.execution_arn}/*/*"
}

# ============================================
# Deployment y Stage
# ============================================

# Deployment: "snapshot" del API en un momento dado
resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.tasks_api.id
  
  # Forzamos re-deployment cuando cambia cualquier método
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.tasks.id,
      aws_api_gateway_method.get_tasks.id,
      aws_api_gateway_method.post_tasks.id,
      aws_api_gateway_method.put_task.id,
      aws_api_gateway_method.delete_task.id,
      aws_api_gateway_integration.get_tasks_integration.id,
      aws_api_gateway_integration.post_tasks_integration.id,
      aws_api_gateway_integration.put_task_integration.id,
      aws_api_gateway_integration.delete_task_integration.id,
    ]))
  }
  
  lifecycle {
    create_before_destroy = true
  }
}

# Stage: ambiente donde se publica el deployment
resource "aws_api_gateway_stage" "api_stage" {
  deployment_id = aws_api_gateway_deployment.api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.tasks_api.id
  stage_name    = var.environment  # "dev", "staging", "prod"
  
  depends_on = [aws_api_gateway_account.main]
  
  # Configuración de logging (útil para debug)
  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway_logs.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      resourcePath   = "$context.resourcePath"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
    })
  }
  
  # X-Ray tracing para debugging
  xray_tracing_enabled = true
}

# CloudWatch Log Group para API Gateway
resource "aws_cloudwatch_log_group" "api_gateway_logs" {
  name              = "/aws/apigateway/${var.project_name}-${var.environment}"
  retention_in_days = 7  # Logs por 7 días (gratis hasta 5GB)
}