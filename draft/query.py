import boto3

dynamodb = boto3.resource('dynamodb')

table1 = dynamodb.Table('run-test-fail-app')
table2 = dynamodb.Table('success-run')

ids_table1 = set()
ids_table2 = set()

# Scan table1 and store all IDs in a set
response = table1.scan()
for item in response['Items']:
    ids_table1.add(item['appId'])

# Scan table2 and store all IDs in a set
response = table2.scan()
for item in response['Items']:
    ids_table2.add(item['appId'])

# Check if the sets are equal
if ids_table1 == ids_table2:
    print("Both tables have the same IDs")
else:
    print("The tables do not have the same IDs")
