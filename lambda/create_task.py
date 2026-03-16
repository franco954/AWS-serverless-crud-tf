"""
Lambda Function: POST /tasks
Descripción: Crea una nueva tarea en DynamoDB

Event structure:
{
    "httpMethod": "POST",
    "body": "{\"title\": \"Mi tarea\", \"description\": \"Descripción\"}"
}
"""

import json
import boto3
import os
import uuid
from datetime import datetime

# Cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)


def lambda_handler(event, context):
    """
    Crea una nueva tarea
    
    Body esperado:
    {
        "title": "string (requerido)",
        "description": "string (opcional)"
    }
    """
    
    try:
        # Parse del body (viene como string JSON)
        if not event.get('body'):
            return error_response(400, 'Body vacío')
        
        body = json.loads(event['body'])
        
        # Validación de campos requeridos
        if not body.get('title'):
            return error_response(400, 'El campo "title" es requerido')
        
        if len(body['title'].strip()) == 0:
            return error_response(400, 'El título no puede estar vacío')
        
        # Construcción del item
        task = {
            'taskId': str(uuid.uuid4()),  # ID único
            'title': body['title'].strip(),
            'description': body.get('description', '').strip(),
            'completed': False,
            'createdAt': int(datetime.now().timestamp()),  # Unix timestamp
            'updatedAt': int(datetime.now().timestamp())
        }
        
        # Guardar en DynamoDB
        table.put_item(Item=task)
        
        # Log exitoso
        print(f"Tarea creada: {task['taskId']} - {task['title']}")
        
        # Response exitoso
        return {
            'statusCode': 201,  # 201 Created
            'headers': get_cors_headers(),
            'body': json.dumps({
                'message': 'Tarea creada exitosamente',
                'task': task
            })
        }
        
    except json.JSONDecodeError:
        return error_response(400, 'Body JSON inválido')
    
    except Exception as e:
        print(f"Error al crear tarea: {str(e)}")
        return error_response(500, f'Error interno: {str(e)}')


def error_response(status_code, message):
    """
    Helper para responses de error consistentes
    
    Args:
        status_code: Código HTTP (400, 500, etc)
        message: Mensaje de error
    
    Returns:
        Dict con formato API Gateway
    """
    return {
        'statusCode': status_code,
        'headers': get_cors_headers(),
        'body': json.dumps({
            'error': message
        })
    }


def get_cors_headers():
    """
    Headers CORS estándar
    
    Returns:
        Dict con headers
    """
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }


# Testing local
if __name__ == "__main__":
    test_event = {
        "httpMethod": "POST",
        "body": json.dumps({
            "title": "Aprender Terraform",
            "description": "Hacer un proyecto serverless en AWS"
        })
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))