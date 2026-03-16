# ============================================
# IAM Role para Lambda
# ============================================

# Assume Role Policy: quién puede asumir este role
data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"
    
    # Lambda service puede asumir este role
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    
    actions = ["sts:AssumeRole"]
  }
}

# El role en sí
resource "aws_iam_role" "lambda_role" {
  name               = "${var.project_name}-${var.environment}-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

# ============================================
# Policy: Permisos para DynamoDB
# ============================================

data "aws_iam_policy_document" "lambda_dynamodb_policy" {
  # Permisos para leer/escribir en DynamoDB
  statement {
    effect = "Allow"
    
    actions = [
      "dynamodb:GetItem",      # Leer un item
      "dynamodb:PutItem",      # Crear/actualizar item
      "dynamodb:UpdateItem",   # Actualizar item
      "dynamodb:DeleteItem",   # Borrar item
      "dynamodb:Scan",         # Scan tabla (costoso!)
      "dynamodb:Query"         # Query con índices
    ]
    
    # Solo en ESTA tabla específica
    resources = [
      aws_dynamodb_table.tasks.arn
    ]
  }
}

# Crear la policy
resource "aws_iam_policy" "lambda_dynamodb_policy" {
  name        = "${var.project_name}-${var.environment}-lambda-dynamodb"
  description = "Permite a Lambda acceder a DynamoDB"
  policy      = data.aws_iam_policy_document.lambda_dynamodb_policy.json
}

# Attachear la policy al role
resource "aws_iam_role_policy_attachment" "lambda_dynamodb_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_dynamodb_policy.arn
}

# ============================================
# Policy: CloudWatch Logs (logging)
# ============================================

# AWS tiene una policy managed para logs básicos
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}