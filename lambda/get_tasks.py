"""
Lambda Function: GET /tasks
Descripción: Obtiene todas las tareas del usuario autenticado

Event structure incluye claims de Cognito:
{
    "requestContext": {
        "authorizer": {
            "claims": {
                "sub": "user-id-uuid",
                "email": "user@example.com"
            }
        }
    }
}
"""

import json
import boto3
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)


def lambda_handler(event, context):
    """
    Obtiene todas las tareas del usuario autenticado
    """
    try:
        # Extraer userId del token JWT (Cognito)
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        print(f"Getting tasks for user: {user_id}")
        
        # Query DynamoDB por userId (partition key)
        response = table.query(
            KeyConditionExpression='userId = :uid',
            ExpressionAttributeValues={
                ':uid': user_id
            }
        )
        
        tasks = response.get('Items', [])
        
        print(f"Found {len(tasks)} tasks for user {user_id}")
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'tasks': convert_decimals(tasks),
                'count': len(tasks)
            })
        }
        
    except KeyError as e:
        print(f"Error: Missing authorization context - {str(e)}")
        return {
            'statusCode': 401,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'error': 'Unauthorized - No valid token provided'
            })
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}'
            })
        }


def get_cors_headers():
    """Headers CORS"""
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }


def convert_decimals(obj):
    """Convierte Decimal de DynamoDB a int/float"""
    from decimal import Decimal
    
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    else:
        return obj