import json
import os
from .desired_cap import AndroidDesiredCapabilities
from .device_controller import DeviceController
from .app_controller import AppController
import time


class DynamicTestingApplication:
    def __init__(self, udid, version, system_port=8200, proxy_port=8080, appium_port=4723):
        self.desired_cap = AndroidDesiredCapabilities.generate(
            udid, version, system_port, proxy_port, appium_port)
        self.device_udid = udid
        self.on_perform = lambda app_controller: None
        self.setup_folder()
        self.device_controller = DeviceController(udid)

    def __debug(self, app_controller: AppController):
        print('Entering debug mode')
        while True:
            inp = input().strip()
            if inp in ["q", "quit"]:
                break
            elif inp in ["s", "source"]:
                source = app_controller.get_page_source()
                print(source)
            elif inp in ["h", "help"]:
                print("Press q to exit")
            elif inp in ["hq"]:
                print("Highlevel query")
                method = input("Method to be called: ")
                try:
                    print(getattr(app_controller.highlevel_query, method)())
                except Exception as err:
                    print(err)
            else:
                print("Command", inp, "not found")

    def setup_folder(self):
        os.system("mkdir log")
        os.system("mkdir result")
        os.system("mkdir log_mitm")

    def set_env_path(self, android_sdk_root=None, java_home=None):
        """Call this method before performing test if there are errors about environment path"""
        if android_sdk_root and 'ANDROID_SDK_ROOT' not in os.environ:
            os.environ['ANDROID_SDK_ROOT'] = android_sdk_root

        if java_home and 'JAVA_HOME' not in os.environ:
            os.environ['JAVA_HOME'] = java_home

    def set_on_perform(self, function):
        """Set function to perform on each loop. 
        The function receive AppController as a argument"""
        self.on_perform = function

    def set_action_count(self, action_count):
        self.action_count = action_count

    def test(self, apk_path, action_count=10, install=True, debug=False, activity=None):
        if not self.device_controller.is_online():
            raise Exception('The testing device is offine')

        extended_desired_cap = self.desired_cap
        if install:
            extended_desired_cap["app"] = apk_path
            self.device_controller.install_apk(apk_path)

        app_controller = AppController(
            extended_desired_cap, apk_path, activity)

        if hasattr(self, 'action_count'):
            action_count = self.action_count

        if debug:
            self.__debug(app_controller)
        else:
            for i in range(action_count):
                print(i)
                self.on_perform(app_controller)
                time.sleep(1)
