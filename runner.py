import os
import argparse
import boto3
from boto3.dynamodb.conditions import Key, Attr

parser = argparse.ArgumentParser()
parser.add_argument('device_name', metavar='device_name',
                    type=str, help='Device UDID or IP address')
parser.add_argument('proxy_host', metavar='proxy_host',
                    type=str, help='Proxy host')
parser.add_argument('additional_arg', metavar='additional_arg',
                    type=str, help='additional_arg')

if __name__ == "__main__":
    args = parser.parse_args()
    # to set before run
    proxyHost = args.proxy_host
    deviceName = args.device_name
    additionalArg = args.additional_arg
    # ------ python3 runner.py emulator-5554 192.168.10.167 '--appium_port 8201'
    dynamo_client = boto3.client("dynamodb")
    tableName = 'new-application-info'
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(tableName)
    """ response =  table.scan(
                Limit=10,
                FilterExpression='appCategory = :value',
                ExpressionAttributeValues={':value': 'AUTO_AND_VEHICLES'}
            ) """
    response =  table.scan(
                Limit=1
            )
    for item in response['Items']:
        appId = item['appId']
        #os.system(f'python3 main.py emulator-5554 {item} 10.18.76.108 --appium_port 8201')
        print(f'python3 main.py {deviceName} {appId} {proxyHost} {additionalArg}')
        #os.system(f'python3 main.py emulator-5554 {id} 192.168.10.167 --appium_port 8201')
