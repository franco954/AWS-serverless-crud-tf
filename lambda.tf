# ============================================
# Lambda: GET Tasks (leer todas las tareas)
# ============================================

# Primero: comprimimos el código Python en un .zip
data "archive_file" "get_tasks_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda/get_tasks.py"
  output_path = "${path.module}/lambda/get_tasks.zip"
}

# Recurso Lambda
resource "aws_lambda_function" "get_tasks" {
  # Nombre de la función
  filename      = data.archive_file.get_tasks_zip.output_path
  function_name = "${var.project_name}-${var.environment}-get-tasks"
  
  # IAM role que define permisos
  role = aws_iam_role.lambda_role.arn
  
  # Handler: archivo.función
  # get_tasks.py tiene una función llamada lambda_handler
  handler = "get_tasks.lambda_handler"
  
  # Hash del archivo - Terraform detecta cambios en el código
  source_code_hash = data.archive_file.get_tasks_zip.output_base64sha256
  
  # Runtime - versión de Python
  runtime = "python3.11"
  
  # Timeout en segundos - máximo 900 (15 min)
  timeout = 10
  
  # Memoria en MB - de 128 a 10240
  # Más memoria = más CPU (y más caro)
  memory_size = 128
  
  # Variables de entorno que la Lambda puede leer
  environment {
    variables = {
      TABLE_NAME  = aws_dynamodb_table.tasks.name
      ENVIRONMENT = var.environment
    }
  }
}

# ============================================
# Lambda: POST Task (crear tarea)
# ============================================

data "archive_file" "create_task_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda/create_task.py"
  output_path = "${path.module}/lambda/create_task.zip"
}

resource "aws_lambda_function" "create_task" {
  filename         = data.archive_file.create_task_zip.output_path
  function_name    = "${var.project_name}-${var.environment}-create-task"
  role            = aws_iam_role.lambda_role.arn
  handler         = "create_task.lambda_handler"
  source_code_hash = data.archive_file.create_task_zip.output_base64sha256
  runtime         = "python3.11"
  timeout         = 10
  memory_size     = 128
  
  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.tasks.name
    }
  }
}

# ============================================
# Lambda: PUT Task (actualizar tarea)
# ============================================

data "archive_file" "update_task_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda/update_task.py"
  output_path = "${path.module}/lambda/update_task.zip"
}

resource "aws_lambda_function" "update_task" {
  filename         = data.archive_file.update_task_zip.output_path
  function_name    = "${var.project_name}-${var.environment}-update-task"
  role            = aws_iam_role.lambda_role.arn
  handler         = "update_task.lambda_handler"
  source_code_hash = data.archive_file.update_task_zip.output_base64sha256
  runtime         = "python3.11"
  timeout         = 10
  memory_size     = 128
  
  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.tasks.name
    }
  }
}


data "archive_file" "delete_task_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda/delete_task.py"
  output_path = "${path.module}/lambda/delete_task.zip"
}

resource "aws_lambda_function" "delete_task" {
  filename         = data.archive_file.delete_task_zip.output_path
  function_name    = "${var.project_name}-${var.environment}-delete-task"
  role            = aws_iam_role.lambda_role.arn
  handler         = "delete_task.lambda_handler"
  source_code_hash = data.archive_file.delete_task_zip.output_base64sha256
  runtime         = "python3.11"
  timeout         = 10
  memory_size     = 128
  
  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.tasks.name
    }
  }
}