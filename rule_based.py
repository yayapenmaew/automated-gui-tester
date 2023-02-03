#!/usr/bin/env python3
from tester.application import DynamicTestingApplication
from tester.app_controller import AppController
from tester.rules.rules import initialize_rules
from tester.rules.visual_state import VisualState, VisualStateGraph, ETVisualState
from collections import defaultdict
import threading
import time
import logging
import matplotlib.pyplot as plt
import logging
import argparse
import os
from tester.exceptions import DynamicTestError, PaidAppError
from dotenv import load_dotenv, find_dotenv
import sys

load_dotenv(find_dotenv())

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

parser.add_argument('--si', metavar="skip_install", type=bool,
                    help="Skip the installation process", default=False)
parser.add_argument('--latest_version', metavar="latest_version", type=str,
                    help="Latest version of the application. The script will terminate \
                    if the downloaded app has the same version as latest_version", default=None)


if __name__ == '__main__':
    args = parser.parse_args()

    os.system('mkdir log_tester')
    logging.basicConfig(format='[%(asctime)s.%(msecs)03d][%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO,
                        handlers=[
                            logging.FileHandler(
                                filename=f"log_tester/{args.app_id}", mode="w"),
                            logging.StreamHandler()
                        ])

    try:
        app = DynamicTestingApplication(
            udid=args.device_name,
            version=args.version,
            proxy_host=args.proxy_host,
            system_port=args.system_port,
            proxy_port=args.proxy_port,
            appium_port=args.appium_port,
            mitm_path=os.environ.get("MITM_PATH"),
        )

        '''In case Appium needs proper env paths'''
        app.set_env_path(
            android_sdk_root=os.environ.get("ANDROID_SDK_ROOT"),
            java_home=os.environ.get("JAVA_HOME")
        )

        action_count = 300 #50
        app.set_action_count(action_count)

        rules = initialize_rules(include=[
            "ViewPagerRule",
            "ImageButtonRule",
            "ActionBarRule",
            "RandomClickElementRule",
            "FillTextFieldsRule",
            "BackToAppRule",
        ])

        def on_perform(app_controller: AppController, step):
            for rule in rules:
                try:
                    if rule.match(app_controller):
                        rule.action(app_controller)
                except KeyboardInterrupt:
                    return
                except:
                    pass

        app.foreach(on_perform)

        installed_packages_before_test = set(
            app.device_controller.get_all_installed_packages())

        app.test(
            args.app_id,
            install_type='playstore',
            reset_state=True,
            latest_version=args.latest_version
        )
    except Exception as exception:
        logging.error(
            'Unexpected error while performing dynamic test', exception)

        '''Delete all dangling apps'''
        installed_packages_after_test = set(
            app.device_controller.get_all_installed_packages())
        packages_to_delete = installed_packages_after_test - installed_packages_before_test
        for orphan_app in packages_to_delete:
            logging.info(f'Deleting orphan app: {orphan_app}')
            app.device_controller.uninstall(orphan_app)

        sys.exit(exception.exit_code)
