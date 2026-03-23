# AWS Serverless CRUD API - Terraform

API REST serverless completamente funcional construida con AWS Lambda, API Gateway, y DynamoDB, deployed con Terraform.

## 🏗️ Arquitectura

```
Cliente → API Gateway → Lambda → DynamoDB
                ↓
         CloudWatch Logs
```

### Servicios AWS utilizados:
- **API Gateway** - REST API endpoints
- **Lambda** - Funciones serverless (Python 3.11)
- **DynamoDB** - Base de datos NoSQL
- **IAM** - Roles y permisos
- **CloudWatch** - Logging y monitoring

## 🚀 Features

- ✅ **GET /tasks** - Listar todas las tareas
- ✅ **POST /tasks** - Crear nueva tarea
- ✅ **PUT /tasks/{id}** - Actualizar tarea existente
- ✅ **CORS** habilitado
- ✅ **CloudWatch Logs** para debugging
- ✅ **100% serverless** - sin servidores que gestionar
- ✅ **Infrastructure as Code** con Terraform

## 📋 Prerequisitos

- [Terraform](https://www.terraform.io/downloads) >= 1.0
- [AWS CLI](https://aws.amazon.com/cli/) configurado
- Cuenta de AWS con credenciales configuradas
- Python 3.11 (para desarrollo local de Lambdas)

## 🛠️ Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU-USUARIO/aws-serverless-crud-terraform.git
cd aws-serverless-crud-terraform
```

### 2. Configurar variables

```bash
# Copiar el archivo de ejemplo
cp example.tfvars terraform.tfvars

# Editar con tus valores
nano terraform.tfvars
```

```hcl
aws_region   = "us-east-1"
environment  = "dev"
project_name = "tasks-api"
```

### 3. Configurar credenciales de AWS

```bash
aws configure
```

### 4. Deployar la infraestructura

```bash
# Inicializar Terraform
terraform init

# Ver el plan de ejecución
terraform plan

# Aplicar cambios
terraform apply
```

Terraform mostrará la URL del API al finalizar:
```
Outputs:
api_url = "https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev/tasks"
```

## 📡 Uso del API

### Listar tareas (GET)

```bash
curl https://TU-API-URL/tasks
```

**Response:**
```json
{
  "tasks": [],
  "count": 0
}
```

### Crear tarea (POST)

```bash
curl -X POST https://TU-API-URL/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mi tarea",
    "description": "Descripción de la tarea"
  }'
```

**Response:**
```json
{
  "message": "Tarea creada exitosamente",
  "task": {
    "taskId": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Mi tarea",
    "description": "Descripción de la tarea",
    "completed": false,
    "createdAt": 1710518400,
    "updatedAt": 1710518400
  }
}
```

### Actualizar tarea (PUT)

```bash
curl -X PUT https://TU-API-URL/tasks/TASK-ID \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true,
    "title": "Tarea completada"
  }'
```

## 📁 Estructura del Proyecto

```
.
├── main.tf                    # Configuración principal de Terraform
├── variables.tf               # Variables de configuración
├── outputs.tf                 # Outputs (API URL, etc.)
├── api_gateway.tf             # Configuración de API Gateway
├── api_gateway_account.tf     # Rol de CloudWatch para API Gateway
├── dynamodb.tf                # Tabla de DynamoDB
├── iam.tf                     # Roles y políticas IAM
├── lambda.tf                  # Funciones Lambda
├── lambda/
│   ├── get_tasks.py           # Lambda para GET
│   ├── create_task.py         # Lambda para POST
│   └── update_task.py         # Lambda para PUT
├── .gitignore
└── README.md
```

## 💰 Costos

Con el Free Tier de AWS, este proyecto es **100% gratuito** mientras:
- Hagas < 1M requests/mes (API Gateway)
- Ejecutes < 1M invocaciones Lambda/mes
- Almacenes < 25GB en DynamoDB

**Costo estimado en producción:** ~$5-10/mes para tráfico medio.

## 🧹 Limpieza

Para destruir toda la infraestructura:

```bash
terraform destroy
```

⚠️ **Advertencia:** Esto borrará TODOS los recursos, incluyendo los datos en DynamoDB.

## 🔧 Desarrollo Local

### Testing de Lambdas

```bash
cd lambda

# Instalar dependencias
pip install boto3

# Correr tests
python get_tasks.py
```

### Ver logs en CloudWatch

```bash
# Ver logs en tiempo real
aws logs tail /aws/lambda/tasks-api-dev-get-tasks --follow
```

## 📊 Monitoreo

Acceder a métricas en AWS Console:
- **CloudWatch** → Log groups → `/aws/lambda/tasks-api-dev-*`
- **API Gateway** → APIs → tasks-api-dev-api → Stages → dev
- **DynamoDB** → Tables → tasks-api-dev-tasks → Monitoring

## 🚧 Próximas mejoras

- [ ] Agregar endpoint DELETE
- [ ] Autenticación con Cognito
- [ ] CI/CD con GitHub Actions
- [ ] Frontend React
- [ ] DynamoDB Streams para eventos
- [ ] Tests unitarios
- [ ] Custom domain con Route53
