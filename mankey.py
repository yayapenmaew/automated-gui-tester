#!/usr/bin/env python3
from tester.application import DynamicTestingApplication
from tester.app_controller import AppController
import time
import logging
import argparse
import os
from tester.exceptions import DynamicTestError, PaidAppError
from dotenv import load_dotenv, find_dotenv
import sys
import random


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
            # Linux user: plz change this line!
            mitm_path=os.environ.get("MITM_PATH"),
        )

        '''In case Appium needs proper env paths'''
        app.set_env_path(
            android_sdk_root=os.environ.get("ANDROID_SDK_ROOT"),
            java_home=os.environ.get("JAVA_HOME")
        )

        action_count = 200
        app.set_action_count(action_count)

        window_size = ""
        activity_count = 0
        package_count = 0
        start_time = time.time()

        def before(app_controller: AppController):
            global window_size
            time.sleep(10)
            window_size = app_controller.get_window_size()

        def on_perform(app_controller: AppController, step):
            global package_count
            global activity_count
            package = app_controller.get_current_package()
            driver = app_controller.driver

            on_current_package = app_controller.is_on_current_package()

            if(not on_current_package and package_count >= 5):
                activity_count = 0
                try:
                    driver.launch_app()
                except:
                    pass
            else:
                # allow pop-up, browser and default application for 10 actions

                if(not on_current_package):
                    package_count += 1

                if (activity_count >= 50):
                    activity_count = 0

                    try:
                        driver.launch_app()
                    except:
                        pass
                else:
                    try:
                        prev_activity = driver.current_activity
                        Clickable_Elements = driver.find_elements_by_android_uiautomator(
                            "new UiSelector().clickable(true)")
                        Textinput_Elements = []
                        for element in Clickable_Elements:
                            if element.get_attribute("class") == "android.widget.EditText" and element.get_attribute("focusable") == "true":
                                Textinput_Elements.append(element)

                        Clickable_Elements = list(
                            set(Clickable_Elements) - set(Textinput_Elements))
                        # iMonkey
                        # random action  1 - 100
                        if (len(Clickable_Elements) == 0):
                            random_action = random.randrange(81, 101)
                        elif (len(Textinput_Elements) == 0):
                            random_action = random.randrange(21, 101)
                        else:
                            random_action = random.randrange(1, 101)

                        # 0, filled a random text field | or fill all ? 20 %
                        if(random_action < 21):
                            temp = random.randrange(len(Textinput_Elements))
                            app_controller.highlevel_query.fill_text_input()

                        # 1 randomly click on clickable element 60%
                        elif (random_action >= 21 and random_action < 81):
                            temp = random.randrange(len(Clickable_Elements))
                            Clickable_Elements[temp].click()
                        # Monkey
                        # 15 % swipe randomly (4 direction)
                        elif (random_action >= 81 and random_action < 96):
                            height = window_size["height"]
                            width = window_size["width"]
                            temp = random.randrange(4)
                            #driver.swipe(startX, startY, endX, endY, duration)
                            if temp == 0:
                                try:
                                    driver.swipe(width/2, height/2,
                                                 width/2, height/4, 400)
                                except:
                                    driver.swipe(height/2, width/2,
                                                 height/2, width/4, 400)
                            if temp == 1:
                                try:
                                    driver.swipe(width/2, height/2,
                                                 width/2, height*3/4, 400)
                                except:
                                    driver.swipe(height/2, width/2,
                                                 height/2, width*3/4, 400)

                            if temp == 2:
                                try:
                                    driver.swipe(width/2, height/2,
                                                 width/4, height/4, 400)
                                except:
                                    driver.swipe(height/2, width/2,
                                                 height/4, width/4, 400)

                            if temp == 3:
                                try:
                                    driver.swipe(width/2, height/2,
                                                 width*3/4, height/4, 400)
                                except:
                                    driver.swipe(height/2, width/2,
                                                 height*3/4, width/4, 400)

                        # 5% monkey
                        elif (random_action >= 96):
                            temp = random.randrange(2)
                            if temp == 0:
                                app_controller.random_touch()
                            if temp == 1:
                                driver.press_keycode(4)

                    except:
                        try:
                            driver.launch_app()
                        except:
                            pass

                    curr_activity = driver.current_activity

                    if(curr_activity == prev_activity):
                        activity_count += 1


        app.foreach(on_perform)

        installed_packages_before_test = set(
            app.device_controller.get_all_installed_packages())

        app.test(
            args.app_id,
            install_type='playstore',
            reset_state=False,
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
