import argparse
from device_controller import DeviceController

parser = argparse.ArgumentParser()
parser.add_argument('device_name', metavar='device_name',
                    type=str, help='Device UDID or IP address')           
parser.add_argument('app_name', metavar='app_name',
                    type=str, help='app_name')


if __name__ == "__main__":
    args = parser.parse_args()
    # to set before run
    deviceName = args.device_name
    appName = args.app_name
    deviceController = DeviceController(deviceName)
    d = deviceController.uninstall(appName)
    