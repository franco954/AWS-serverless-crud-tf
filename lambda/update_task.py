"""
Lambda Function: PUT /tasks/{id}
Descripción: Actualiza una tarea existente en DynamoDB

Event structure:
{
    "httpMethod": "PUT",
    "pathParameters": {"id": "task-uuid"},
    "body": "{\"title\": \"...\", \"completed\": true}"
}
"""

import json
import boto3
import os
from datetime import datetime
from boto3.dynamodb.conditions import Key

# Cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)


def lambda_handler(event, context):
    """
    Actualiza una tarea existente
    
    Path parameter:
        id: taskId de la tarea
    
    Body (todos opcionales):
    {
        "title": "string",
        "description": "string",
        "completed": boolean
    }
    """
    
    try:
        # Obtener el ID del path parameter
        task_id = event.get('pathParameters', {}).get('id')
        
        if not task_id:
            return error_response(400, 'ID de tarea no proporcionado')
        
        # Parse del body
        if not event.get('body'):
            return error_response(400, 'Body vacío')
        
        body = json.loads(event['body'])
        
        # Verificar que la tarea existe
        existing_task = table.get_item(Key={'taskId': task_id})
        
        if 'Item' not in existing_task:
            return error_response(404, f'Tarea con ID {task_id} no encontrada')
        
        # Construir expresión de update
        # Solo actualizamos campos que vienen en el body
        update_expression_parts = []
        expression_attribute_values = {}
        expression_attribute_names = {}
        
        # Actualizar title si viene
        if 'title' in body:
            if not body['title'] or len(body['title'].strip()) == 0:
                return error_response(400, 'El título no puede estar vacío')
            
            update_expression_parts.append('#title = :title')
            expression_attribute_values[':title'] = body['title'].strip()
            expression_attribute_names['#title'] = 'title'
        
        # Actualizar description si viene
        if 'description' in body:
            update_expression_parts.append('#desc = :desc')
            expression_attribute_values[':desc'] = body['description'].strip()
            expression_attribute_names['#desc'] = 'description'
        
        # Actualizar completed si viene
        if 'completed' in body:
            if not isinstance(body['completed'], bool):
                return error_response(400, 'El campo "completed" debe ser booleano')
            
            update_expression_parts.append('completed = :completed')
            expression_attribute_values[':completed'] = body['completed']
        
        # Siempre actualizar updatedAt
        update_expression_parts.append('updatedAt = :updatedAt')
        expression_attribute_values[':updatedAt'] = int(datetime.now().timestamp())
        
        # Si no hay nada que actualizar
        if len(update_expression_parts) == 1:  # Solo updatedAt
            return error_response(400, 'No hay campos para actualizar')
        
        # Construir la expresión completa
        update_expression = 'SET ' + ', '.join(update_expression_parts)
        
        # Ejecutar update
        response = table.update_item(
            Key={'taskId': task_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names if expression_attribute_names else None,
            ReturnValues='ALL_NEW'  # Devuelve el item actualizado
        )
        
        updated_task = response['Attributes']
        
        # Log
        print(f"Tarea actualizada: {task_id}")
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'message': 'Tarea actualizada exitosamente',
                'task': convert_decimals(updated_task)
            })
        }
        
    except json.JSONDecodeError:
        return error_response(400, 'Body JSON inválido')
    
    except Exception as e:
        print(f"Error al actualizar tarea: {str(e)}")
        return error_response(500, f'Error interno: {str(e)}')


def error_response(status_code, message):
    """Helper para responses de error"""
    return {
        'statusCode': status_code,
        'headers': get_cors_headers(),
        'body': json.dumps({'error': message})
    }


def get_cors_headers():
    """Headers CORS estándar"""
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }


def convert_decimals(obj):
    """Convierte Decimal a int/float para JSON"""
    from decimal import Decimal
    
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj


# Testing local
if __name__ == "__main__":
    test_event = {
        "httpMethod": "PUT",
        "pathParameters": {
            "id": "test-task-id"
        },
        "body": json.dumps({
            "title": "Tarea actualizada",
            "completed": True
        })
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))