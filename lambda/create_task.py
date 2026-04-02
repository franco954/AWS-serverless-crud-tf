"""
Lambda Function: POST /tasks
Descripción: Crea una nueva tarea para el usuario autenticado
"""

import json
import boto3
import os
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)


def lambda_handler(event, context):
    """
    Crea una nueva tarea
    """
    try:
        # Extraer userId del token
        user_id = event['requestContext']['authorizer']['claims']['sub']
        user_email = event['requestContext']['authorizer']['claims'].get('email', 'unknown')
        
        # Parsear body
        body = json.loads(event['body'])
        
        # Validar campos requeridos
        if 'title' not in body:
            return error_response(400, 'Title is required')
        
        # Crear tarea
        task_id = str(uuid.uuid4())
        timestamp = int(datetime.now().timestamp())
        
        task = {
            'userId': user_id,  # Partition key
            'taskId': task_id,  # Sort key
            'title': body['title'],
            'description': body.get('description', ''),
            'completed': body.get('completed', False),
            'createdAt': timestamp,
            'updatedAt': timestamp,
            'createdBy': user_email  # Info adicional
        }
        
        # Guardar en DynamoDB
        table.put_item(Item=task)
        
        print(f"Task created: {task_id} for user {user_id}")
        
        return {
            'statusCode': 201,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'message': 'Task created successfully',
                'task': task
            })
        }
        
    except KeyError:
        return error_response(401, 'Unauthorized')
    except json.JSONDecodeError:
        return error_response(400, 'Invalid JSON in request body')
    except Exception as e:
        print(f"Error: {str(e)}")
        return error_response(500, f'Internal server error: {str(e)}')


def error_response(status_code, message):
    return {
        'statusCode': status_code,
        'headers': get_cors_headers(),
        'body': json.dumps({'error': message})
    }


def get_cors_headers():
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }