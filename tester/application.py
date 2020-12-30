import json
import os
from .desired_cap import AndroidDesiredCapabilities
from .device_controller import DeviceController
from .app_controller import AppController


class DynamicTestingApplication:
    def __init__(self, udid, version, system_port=8200, proxy_port=8080, appium_port=4723):
        self.desired_cap = AndroidDesiredCapabilities.generate(
            udid, version, system_port, proxy_port, appium_port)
        self.device_udid = udid
        self.on_perform = lambda app_controller: None
        self.setup_folder()
        self.device_controller = DeviceController(udid)
        print(self.device_controller.is_online())

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

    def test(self, apk_path, action_count=10, install=True):
        if not self.device_controller.is_online():
            raise Exception('The testing device is offine')

        if install:
            self.device_controller.install_apk(apk_path)

        app_controller = AppController(self.desired_cap, apk_path)

        if hasattr(self, 'action_count'):
            action_count = self.action_count

        for i in range(action_count):
            self.on_perform(app_controller)
