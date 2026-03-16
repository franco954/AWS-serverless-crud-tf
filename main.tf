
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"  
    }
  }
}

provider "aws" {
  region = var.aws_region  # Lee la región de variables.tf
  
  default_tags {
    tags = {
      Project     = "ServerlessCRUD"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}