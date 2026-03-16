"""
Lambda Function: DELETE /tasks/{id}
Descripción: Borra una tarea de DynamoDB

Event structure:
{
    "httpMethod": "DELETE",
    "pathParameters": {"id": "task-uuid"}
}
"""

import json
import boto3
import os

# Cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)


def lambda_handler(event, context):
    """
    Borra una tarea existente
    
    Path parameter:
        id: taskId de la tarea a borrar
    
    Returns:
        200: Tarea borrada exitosamente
        404: Tarea no encontrada
        500: Error interno
    """
    
    try:
        # Obtener el ID del path parameter
        task_id = event.get('pathParameters', {}).get('id')
        
        if not task_id:
            return error_response(400, 'ID de tarea no proporcionado')
        
        # Verificar que la tarea existe ANTES de intentar borrarla
        # Esto previene borrar algo que no existe y da mejor feedback
        try:
            existing_task = table.get_item(Key={'taskId': task_id})
        except Exception as e:
            print(f"Error al buscar tarea: {str(e)}")
            return error_response(500, f'Error al buscar tarea: {str(e)}')
        
        if 'Item' not in existing_task:
            return error_response(404, f'Tarea con ID {task_id} no encontrada')
        
        # Guardar info de la tarea antes de borrarla (para el response)
        deleted_task = existing_task['Item']
        
        # Borrar la tarea
        try:
            table.delete_item(Key={'taskId': task_id})
        except Exception as e:
            print(f"Error al borrar tarea: {str(e)}")
            return error_response(500, f'Error al borrar tarea: {str(e)}')
        
        # Log exitoso
        print(f"Tarea borrada: {task_id} - {deleted_task.get('title', 'Sin título')}")
        
        # Response exitoso con la tarea que se borró
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'message': 'Tarea borrada exitosamente',
                'deletedTask': convert_decimals(deleted_task)
            })
        }
        
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return error_response(500, f'Error interno: {str(e)}')


def error_response(status_code, message):
    """
    Helper para responses de error consistentes
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
    """
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }


def convert_decimals(obj):
    """
    Convierte objetos Decimal de DynamoDB a int/float para JSON
    """
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
        "httpMethod": "DELETE",
        "pathParameters": {
            "id": "test-task-id"
        }
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))