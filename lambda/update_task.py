"""
Lambda Function: PUT /tasks/{id}
Descripción: Actualiza una tarea del usuario (con validación de ownership)
"""

import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)


def lambda_handler(event, context):
    """
    Actualiza una tarea existente
    """
    try:
        # Extraer userId y taskId
        user_id = event['requestContext']['authorizer']['claims']['sub']
        task_id = event['pathParameters']['id']
        
        # Parsear body
        body = json.loads(event['body'])
        
        # Verificar que la tarea existe y pertenece al usuario
        existing_task = table.get_item(
            Key={
                'userId': user_id,
                'taskId': task_id
            }
        )
        
        if 'Item' not in existing_task:
            return error_response(404, 'Task not found or you do not have permission')
        
        # Construir expression de update
        update_expr = "SET updatedAt = :now"
        expr_values = {':now': int(datetime.now().timestamp())}
        
        if 'title' in body:
            update_expr += ", title = :title"
            expr_values[':title'] = body['title']
        
        if 'description' in body:
            update_expr += ", description = :desc"
            expr_values[':desc'] = body['description']
        
        if 'completed' in body:
            update_expr += ", completed = :comp"
            expr_values[':comp'] = body['completed']
        
        # Update
        response = table.update_item(
            Key={
                'userId': user_id,
                'taskId': task_id
            },
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_values,
            ReturnValues='ALL_NEW'
        )
        
        print(f"Task updated: {task_id} for user {user_id}")
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'message': 'Task updated successfully',
                'task': convert_decimals(response['Attributes'])
            })
        }
        
    except KeyError:
        return error_response(401, 'Unauthorized')
    except json.JSONDecodeError:
        return error_response(400, 'Invalid JSON')
    except Exception as e:
        print(f"Error: {str(e)}")
        return error_response(500, str(e))


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


def convert_decimals(obj):
    from decimal import Decimal
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    else:
        return obj