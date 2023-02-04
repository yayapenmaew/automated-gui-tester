import os
import argparse
import boto3

parser = argparse.ArgumentParser()
parser.add_argument('device_name', metavar='device_name',
                    type=str, help='Device UDID or IP address')
parser.add_argument('proxy_host', metavar='proxy_host',
                    type=str, help='Proxy host')
parser.add_argument('ex_start', metavar='ex_start',
                    type=str, help='ex_start')
parser.add_argument('additional_arg', metavar='additional_arg',
                    type=str, help='additional_arg')

if __name__ == "__main__":
    args = parser.parse_args()
    # to set before run
    proxyHost = args.proxy_host
    deviceName = args.device_name
    ex_start = args.ex_start
    additionalArg = args.additional_arg
    num_run = 250 #number of app to test
    # ------ python3 runner.py emulator-5554 192.168.10.167 com.mercariapp.mercari '--appium_port 8201'
    dynamo_client = boto3.client("dynamodb")
    tableName = 'new-application-info'
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(tableName)
    response =  table.scan(
                Limit=num_run,
                ExclusiveStartKey={'appId': ex_start}
            )
    #print(response['LastEvaluatedKey']['appId'])
    print('Count',response['Count'])
    for item in response['Items']:
        appId = item['appId']
        #print(f'python3 main.py {deviceName} {appId} {proxyHost} {additionalArg}')
        os.system(f'python3 main.py {deviceName} {appId} {proxyHost} {additionalArg}')
