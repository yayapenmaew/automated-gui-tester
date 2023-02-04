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
