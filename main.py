import argparse
import subprocess as sub
import threading
import os
import pathlib
import time
import json
from analyzer.PI_detection import VULPIXAnalyzer
from tester.exceptions import TimeOutError, VULPIXAnalyzerError, ExternalInterfaceError
from interfaces.external import ExternalOutputInterface
import logging

TIMEOUT_SEC = 5 * 60


class RunCmd(threading.Thread):
    def __init__(self, cmd, timeout, result_interface=None):
        threading.Thread.__init__(self)
        self.cmd = cmd
        self.timeout = timeout

    def run(self):
        self.p = sub.Popen(self.cmd)
        self.p.wait()

    def Run(self):
        self.start()
        self.join(self.timeout)

        if self.is_alive():
            self.p.terminate()      # use self.p.kill() if process needs a kill -9
            self.join()

            if result_interface:
                result_interface.send_error(TimeOutError)
            raise TimeOutError
        elif self.p.returncode != 0:
            raise Exception(
                f"Unexpected error on the tester subprocess. The error details are saved to log file.")


parser = argparse.ArgumentParser()

parser.add_argument('device_name', metavar='device_name',
                    type=str, help='Device UDID or IP address')
parser.add_argument('app_id', metavar='app_id', type=str,
                    help='Application identifier')
parser.add_argument('proxy_host', metavar='proxy_host',
                    type=str, help='Proxy host')

parser.add_argument('--version', metavar='version', type=str,
                    help='Android version', default="7.0")
parser.add_argument('--proxy_port', metavar='proxy_port',
                    type=int, help='Proxy port', default=8080)
parser.add_argument('--system_port', metavar='system_port',
                    type=int, help='System port', default=8200)
parser.add_argument('--appium_port', metavar='appium_port',
                    type=int, help='Appium port', default=4723)

parser.add_argument('--timeout', metavar='timeout',
                    type=int, help='Timeout (second)', default=TIMEOUT_SEC)
parser.add_argument('--endpoint', metavar='endpoint',
                    type=str, help='Endpoint that the result will be sent (Example: 127.0.0.1:80)', default=None)

"""
Example call:
    python3 main.py K6T6R17909001485 com.ookbee.ookbeecomics.android 192.168.1.249
    python3 main.py 192.168.1.41:5555 com.ookbee.ookbeecomics.android 192.168.1.249
"""
if __name__ == '__main__':
    args = parser.parse_args()

    logging.basicConfig(format='[%(asctime)s.%(msecs)03d][%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO,
                        handlers=[
                            logging.StreamHandler()
                        ])
    logging.info(f"Starting main script with following arguments: {args}")

    if args.endpoint:
        result_interface = ExternalOutputInterface(f"http://{args.endpoint}")
    else:
        result_interface = ExternalOutputInterface()

    cmd = [
        'python3',
        './monkey.py',
        args.device_name,
        args.app_id,
        args.proxy_host,
        '--version',
        args.version,
        '--proxy_port',
        str(args.proxy_port),
        '--system_port',
        str(args.system_port),
        '--appium_port',
        str(args.appium_port)
    ]

    RunCmd(cmd, args.timeout, result_interface).Run()

    time.sleep(3)
    try:
        score, result = VULPIXAnalyzer.analyze(args.app_id)
    except:
        result_interface.send_error(VULPIXAnalyzerError)
        raise VULPIXAnalyzerError

    logs_path = {
        "appium": os.path.join(pathlib.Path(__file__).parent.absolute(), 'log_appium', args.app_id + '.log'),
        "mitm": os.path.join(pathlib.Path(__file__).parent.absolute(), 'log_mitm', args.app_id + '.log'),
        "tester": os.path.join(pathlib.Path(__file__).parent.absolute(), 'log_tester', args.app_id),
        "har": os.path.join(pathlib.Path(__file__).parent.absolute(), 'result', args.app_id + '.har'),
        "apk": os.path.join(pathlib.Path(__file__).parent.absolute(), 'apk', args.app_id + '.apk'),
        "app_icon": os.path.join(pathlib.Path(__file__).parent.absolute(), 'app_icons', args.app_id + '.png'),
        "app_info": os.path.join(pathlib.Path(__file__).parent.absolute(), 'app_info', args.app_id + '.json'),
    }

    try:
        with open(logs_path["app_info"]) as fp:
            app_info = json.loads(fp.read())

        result_interface.send_result(
            args.app_id,
            app_info["appLabel"],
            app_info["versionName"],
            args.version,
            score,
            result,
            app_info["developer"],
            logs_path["app_icon"],
            app_info["category"],
            logs_path,
        )
    except:
        result_interface.send_error(ExternalInterfaceError)
        raise ExternalInterfaceError
