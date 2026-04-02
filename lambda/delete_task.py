"""
Lambda Function: DELETE /tasks/{id}
Descripción: Borra una tarea del usuario (con validación de ownership)
"""

import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)


def lambda_handler(event, context):
    """
    Borra una tarea
    """
    try:
        # Extraer userId y taskId
        user_id = event['requestContext']['authorizer']['claims']['sub']
        task_id = event['pathParameters']['id']
        
        # Verificar que existe y pertenece al usuario
        existing_task = table.get_item(
            Key={
                'userId': user_id,
                'taskId': task_id
            }
        )
        
        if 'Item' not in existing_task:
            return error_response(404, 'Task not found or you do not have permission')
        
        # Guardar info antes de borrar
        deleted_task = existing_task['Item']
        
        # Borrar
        table.delete_item(
            Key={
                'userId': user_id,
                'taskId': task_id
            }
        )
        
        print(f"Task deleted: {task_id} for user {user_id}")
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'message': 'Task deleted successfully',
                'deletedTask': convert_decimals(deleted_task)
            })
        }
        
    except KeyError:
        return error_response(401, 'Unauthorized')
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