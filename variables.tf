
variable "aws_region" {
  description = "Región de AWS donde deployar los recursos"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Ambiente de deployment"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
  default     = "tasks-api"
}