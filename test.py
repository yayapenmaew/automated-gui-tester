import os
import boto3

# Define the folder path and DynamoDB table name
folder_path = "./apk"
table_name = "success-run"

# Create a DynamoDB client
dynamodb = boto3.resource('dynamodb')

# Get the DynamoDB table
table = dynamodb.Table(table_name)

# Loop through each file in the folder
for filename in os.listdir(folder_path):
    # Insert the file name into DynamoDB 
    t = filename+''
    appId = os.path.splitext(t)[0] #remove extension
    table.put_item(Item={
        'appId': appId
    })
