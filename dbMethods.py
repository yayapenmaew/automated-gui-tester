import time
import boto3

def storeToTestFailDB(appId, err):
    tableName = 'dynamic-test-fail-appId'
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(tableName)
    response = table.put_item(
    Item={
        'appId':appId,
        'err':err
    }
)

def storeSuccessToDB(appId, device):
    tableName = "success-run"
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(tableName)
    timestamp = time.time()
    readableTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
    table.put_item(Item={
        'appId': appId,
        'device': device,
        'timestamp': readableTime
    })

def checkIfAlreadyRun(appId):
    # Define the DynamoDB table name and the appId to search for
    table_name = "success-run"
    app_id_to_search = appId

    # Create a DynamoDB client
    dynamodb = boto3.resource('dynamodb')

    # Get the DynamoDB table
    table = dynamodb.Table(table_name)

    # Use the get_item() method to retrieve the item with the specified appId key
    response = table.get_item(Key={'appId': app_id_to_search})

    # Check if the item was found
    if 'Item' in response:
        print(f"AppId {app_id_to_search} was found in the {table_name} table.")
        return True
    else:
        print(f"AppId {app_id_to_search} was not found in the {table_name} table.")
        return False

    
