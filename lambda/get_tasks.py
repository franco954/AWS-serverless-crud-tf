"""
Lambda Function: GET /tasks
Descripción: Lista todas las tareas de DynamoDB
 
Event structure (API Gateway Proxy Integration):
{
    "httpMethod": "GET",
    "path": "/tasks",
    "headers": {...},
    "queryStringParameters": {...},
    "body": null
}
"""
 
import json
import boto3
import os
from decimal import Decimal
 
# Cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')
# Lee el nombre de la tabla de variables de entorno
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)
 
 
def lambda_handler(event, context):
    """
    Handler principal de la Lambda
    
    Args:
        event: Evento de API Gateway (dict con httpMethod, body, headers, etc)
        context: Contexto de ejecución de Lambda
    
    Returns:
        Response en formato API Gateway Proxy:
        {
            "statusCode": 200,
            "headers": {...},
            "body": "..." (JSON string)
        }
    """
    
    try:
        # Scan de toda la tabla
        # NOTA: Scan es costoso en tablas grandes. Para producción, usá Query con índices.
        response = table.scan()
        
        # response['Items'] es una lista de dicts
        items = response['Items']
        
        # DynamoDB devuelve Decimal en lugar de int/float
        # Los convertimos a tipos Python normales para JSON
        items = convert_decimals(items)
        
        # Response exitoso
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  # CORS - permite cualquier origen
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({
                'tasks': items,
                'count': len(items)
            })
        }
        
    except Exception as e:
        # Log del error (va a CloudWatch)
        print(f"Error al obtener tareas: {str(e)}")
        
        # Response de error
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Error interno del servidor',
                'message': str(e)
            })
        }
 
 
def convert_decimals(obj):
    """
    Convierte objetos Decimal de DynamoDB a int/float para JSON
    DynamoDB usa Decimal para números, pero json.dumps() no los soporta.
    
    Args:
        obj: Objeto (dict, list, Decimal, etc)
    
    Returns:
        Objeto con Decimals convertidos
    """
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        # Si es entero, devuelve int; sino float
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj
 
 
# Para testing local (opcional)
if __name__ == "__main__":
    # Simula un evento de API Gateway
    test_event = {
        "httpMethod": "GET",
        "path": "/tasks"
    }
    
    # Ejecuta el handler
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))