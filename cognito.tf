# ============================================
# Cognito User Pool
# ============================================

resource "aws_cognito_user_pool" "tasks_pool" {
  name = "${var.project_name}-${var.environment}-users"

  # Configuración de username
  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  # Password policy
  password_policy {
    minimum_length                   = 8
    require_lowercase                = true
    require_uppercase                = true
    require_numbers                  = true
    require_symbols                  = false
    temporary_password_validity_days = 7
  }

  # Account recovery
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  # Email configuration (usando default de Cognito - gratis)
  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }

  # Schema attributes (info adicional del usuario)
  schema {
    name                = "email"
    attribute_data_type = "String"
    required            = true
    mutable             = true

    string_attribute_constraints {
      min_length = 5
      max_length = 255
    }
  }

  # Prevenir borrado accidental
  lifecycle {
    prevent_destroy = false  # Cambiar a true en producción
  }

  tags = {
    Name = "${var.project_name}-user-pool"
  }
}

# ============================================
# Cognito User Pool Client (para la app)
# ============================================

resource "aws_cognito_user_pool_client" "tasks_client" {
  name         = "${var.project_name}-app-client"
  user_pool_id = aws_cognito_user_pool.tasks_pool.id

  # Auth flows permitidos
  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",      # Login con email/password
    "ALLOW_REFRESH_TOKEN_AUTH",      # Renovar tokens
    "ALLOW_USER_SRP_AUTH"            # Secure Remote Password (más seguro)
  ]

  # Token validity
  refresh_token_validity = 30  # días
  access_token_validity  = 60  # minutos
  id_token_validity      = 60  # minutos

  token_validity_units {
    refresh_token = "days"
    access_token  = "minutes"
    id_token      = "minutes"
  }

  # Prevent user existence errors (seguridad)
  prevent_user_existence_errors = "ENABLED"

  # No secrets (para SPAs públicas)
  generate_secret = false

  # Callbacks (opcional - para OAuth)
  # callback_urls = ["http://localhost:3000"]
  # logout_urls   = ["http://localhost:3000"]

  # Scopes
  read_attributes  = ["email"]
  write_attributes = ["email"]
}

# ============================================
# Cognito User Pool Domain (para Hosted UI - opcional)
# ============================================

resource "aws_cognito_user_pool_domain" "tasks_domain" {
  domain       = "${var.project_name}-${var.environment}-auth"
  user_pool_id = aws_cognito_user_pool.tasks_pool.id
}

# ============================================
# Outputs
# ============================================

output "cognito_user_pool_id" {
  description = "ID del User Pool de Cognito"
  value       = aws_cognito_user_pool.tasks_pool.id
}

output "cognito_user_pool_arn" {
  description = "ARN del User Pool"
  value       = aws_cognito_user_pool.tasks_pool.arn
}

output "cognito_client_id" {
  description = "ID del App Client"
  value       = aws_cognito_user_pool_client.tasks_client.id
}

output "cognito_domain" {
  description = "Dominio de Cognito (para Hosted UI)"
  value       = aws_cognito_user_pool_domain.tasks_domain.domain
}