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
parser.add_argument('last_ev', metavar='last_ev',
                    type=str, help='last_ev')                  
parser.add_argument('additional_arg', metavar='additional_arg',
                    type=str, help='additional_arg')

if __name__ == "__main__":
    args = parser.parse_args()
    # to set before run
    proxyHost = args.proxy_host
    deviceName = args.device_name
    exStart = args.ex_start
    lastEv = args.last_ev
    additionalArg = args.additional_arg
    num_run = 5 #number of app to test
    # ------ python3 runner.py emulator-5554 192.168.1.192 logo.maker com.livehousex.lively '--appium_port 8201'
    tableName = 'new-application-info'
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(tableName)
    failTable = dynamodb.Table('new-fail-urls')
    response =  table.scan(
                Limit=num_run,
                ExclusiveStartKey={'appId': exStart}
            )
    print('To be next ExclusiveStartKey',response['LastEvaluatedKey']['appId'])
    print('Count',response['Count'])
    failUrls = failTable.scan(
        ProjectionExpression='appId'
    )['Items']
    failUrlsDict = {}
    for failItems in failUrls:
        failUrlsDict[failItems['appId']] = 1
    count = 1
    appId = ''
    for item in response['Items']:
        if appId:
            os.system(f'python3 tester/del.py {deviceName} {appId}') # to delete the previous app in case it is not deleted (time out error)
        appId = item['appId']
        print("App",{count}, "Start from", {exStart},":", {appId})
        if appId not in failUrlsDict:
            #print(f'python3 main.py {deviceName} {appId} {proxyHost} {additionalArg}')
            os.system(f'python3 main.py {deviceName} {appId} {proxyHost} {additionalArg}')
        if appId == lastEv:
            os.system(f'python3 main.py {deviceName} {appId} {proxyHost} {additionalArg}')
            print('Finish 250')
            break
        count += 1
    print('To be next ExclusiveStartKey',response['LastEvaluatedKey']['appId'])
