import argparse
import subprocess as sub
import threading
import os
import pathlib
import time
import json
from analyzer.PI_detection import VULPIXAnalyzer
from tester.exceptions import EXIT_CODE, TimeOutError, VULPIXAnalyzerError, ExternalInterfaceError, PaidAppError, resolve_exit_code, BadInputError
from interfaces.external import ExternalOutputInterface
from validator.validator import InputValidator
import logging

TIMEOUT_SEC = 15 * 60


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
            logging.error(f"Tester error with returncode {self.p.returncode}")
            try:
                exception = resolve_exit_code(self.p.returncode)
                result_interface.send_error(exception)
                logging.error(exception)
                exit(self.p.returncode)
            except:
                logging.error(
                    f"Unexpected error on the tester subprocess. The error details are saved to log file.")
                exit(self.p.returncode)


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
parser.add_argument('--mode', metavar='mode',
                    type=str, help='Test mode (monkey, ga)', default="ga")
parser.add_argument('--endpoint', metavar='endpoint',
                    type=str, help='Endpoint at which the result will be sent (Example: http://127.0.0.1:80/sendResult)', default=None)
parser.add_argument('--uuid', metavar='uuid',
                    type=str, help='uuid', default=None)
parser.add_argument('--latest_version', metavar="latest_version", type=str,
                    help="Latest version of the application. The script will terminate \
                    if the downloaded app has the same version as latest_version", default=None)
parser.add_argument('--force', dest='force', action="store_true",
                    help='Ignore latest_version checking and force the script to test', default=False)


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
        result_interface = ExternalOutputInterface(f"{args.endpoint}")
    else:
        result_interface = ExternalOutputInterface()

    # Validate inputs
    try:
        if not InputValidator.validate_device_id(args.device_name):
            raise BadInputError('Bad input: device_name')
        if not InputValidator.validate_app_identifier(args.app_id):
            raise BadInputError('Bad input: app_identifier')
        if not InputValidator.validate_version_number(args.version):
            raise BadInputError('Bad input: android_version')
        if not InputValidator.validate_ip_port(args.proxy_host, with_port=False):
            raise BadInputError('Bad input: proxy_host')
    except BadInputError as err:
        result_interface.send_error(err)
        raise err

    try:
        script_to_run = {
            "ga": "rule_based.py",
            "monkey": "monkey.py"
        }[args.mode]
    except:
        raise Exception('Invalid mode. It must be either monkey or ga')

    cmd = [
        'python3',
        script_to_run,
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

    if not args.force and args.latest_version:
        cmd.extend([
            '--latest_version',
            args.latest_version
        ])

    RunCmd(cmd, args.timeout, result_interface).Run()

    time.sleep(10)
    try:
        score, result = VULPIXAnalyzer.analyze(args.app_id,PI_file_path="PI.json", har_file=f"result-{args.device_name}/{args.app_id}.har")
    except:
        result_interface.send_error(VULPIXAnalyzerError)
        logging.error(VULPIXAnalyzerError)
        exit(EXIT_CODE.ANALYZER_ERROR)

    logs_path = {
        "appium": os.path.join(pathlib.Path(__file__).parent.absolute(), 'log_appium', args.app_id + '.log'),
        "mitm": os.path.join(pathlib.Path(__file__).parent.absolute(), 'log_mitm', args.app_id + '.log'),
        "tester": os.path.join(pathlib.Path(__file__).parent.absolute(), 'log_tester', args.app_id),
        "har": os.path.join(pathlib.Path(__file__).parent.absolute(), 'result-'+args.device_name, args.app_id + '.har'), #change here ja
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
            args.uuid
        )
    except:
        result_interface.send_error(ExternalInterfaceError)
        logging.error(ExternalInterfaceError)
        exit(EXIT_CODE.EXTERNAL_INTERFACE_ERROR)
