import json
import os
from .desired_cap import AndroidDesiredCapabilities
from .device_controller import DeviceController
from .app_controller import AppController
from .mitm_controller import ProxyController
from .debugger import Debugger
from .highlevel_query import Widget
import time
import re
import logging
from progressbar import progressbar
from .exceptions import DeviceOfflineError, GamesNotSupportedError, NotSupportedError, PaidAppError
from .playstore_helper import get_cat_slug


class DynamicTestingApplication:
    def __init__(
        self,
        udid,
        version,
        proxy_host,
        system_port=8200,
        proxy_port=8080,
        appium_port=4723,
        mitm_path=os.environ.get("MITM_PATH")
    ):
        self.desired_cap = AndroidDesiredCapabilities.generate(
            udid, version, system_port, proxy_port, appium_port)
        self.proxy_host = proxy_host
        self.device_udid = udid
        self.on_perform = lambda app_controller: None
        self.on_before = lambda app_controller: None
        self.setup_folder()
        self.device_controller = DeviceController(udid)

    def __debug(self, app_controller: AppController):
        print('Entering debug mode')
        while True:
            inp = input().strip()
            if not Debugger.debug(app_controller, inp):
                break

    def setup_folder(self):
        os.system("mkdir log_appium")
        os.system("mkdir result")
        os.system("mkdir log_mitm")
        os.system("mkdir log_tester")
        os.system("mkdir apk")
        os.system("mkdir app_icons")
        os.system("mkdir app_info")

    def set_env_path(self, android_sdk_root=None, java_home=None):
        """Call this method before performing test if there are errors about environment path"""
        if android_sdk_root and 'ANDROID_SDK_ROOT' not in os.environ:
            os.environ['ANDROID_SDK_ROOT'] = android_sdk_root

        if java_home and 'JAVA_HOME' not in os.environ:
            os.environ['JAVA_HOME'] = java_home

    def foreach(self, function):
        """Set function to perform on each loop.
        The function receive AppController as a argument"""
        self.on_perform = function

    def before(self, function):
        self.on_before = function

    def set_action_count(self, action_count):
        self.action_count = action_count

    def install_via_playstore(self, package_name):
        if not self.device_controller.is_online():
            raise Exception('The testing device is offine')

        logging.info(f"Installing {package_name} via Playstore")

        PLAYSTORE_PACKAGE_NAME = 'com.android.vending'
        PLAYSTORE_ACTIVITY = 'com.android.vending.AssetBrowserActivity'
        app_controller = AppController(
            self.desired_cap, PLAYSTORE_PACKAGE_NAME, PLAYSTORE_ACTIVITY)
        app_controller.delay(3)

        '''Click on search bar'''
        search_box = []
        while not search_box:
            search_box = app_controller.highlevel_query.find_by_classname(Widget.TEXT_VIEW, {
                "text": re.compile("Search", re.IGNORECASE)
            })
        search_box[0].click()
        app_controller.delay(2)

        '''Enter app identifier into the search bar'''
        search_bar = app_controller.highlevel_query.find_by_classname(
            Widget.EDIT_TEXT, {"focusable": True})[0]
        search_bar.send_keys(package_name)

        '''Click enter to search'''
        ENTER_KEYCODE = 66
        app_controller.send_key_event(ENTER_KEYCODE)
        app_controller.delay(3)

        '''Click the first search result which is not an Ads'''
        results = []
        while not results:
            results = app_controller.highlevel_query.find_by_classname(
                Widget.LINEAR_LAYOUT, {"clickable": True})
            app_controller.delay(3)

        '''Skip advertisement and suggestion results'''
        result_offset = len(app_controller.highlevel_query.find_by_classname(
            Widget.VIEW, {"contentDescription": re.compile("\nAd\n")}))
        result_offset += len(app_controller.highlevel_query.find_by_classname(
            Widget.TEXT_VIEW, {"text": "Did you mean:"}))

        results[result_offset].click()
        app_controller.delay(3)

        '''Retrieve app information'''
        logging.info('Retrieving app info')
        app_info = app_controller.highlevel_query.find_by_classname(
            Widget.TEXT_VIEW)[:2]
        app_name, dev_name = list(
            map(lambda elem: elem.get_attribute('text'), app_info))
        logging.info(f"{app_name} ({dev_name})")
        app_tags = app_controller.highlevel_query.find_by_classname(
            Widget.BUTTON)
        app_tags = list(map(lambda elem: elem.get_attribute('text'), app_tags))
        app_cat = get_cat_slug(app_tags)
        logging.info(f"Tags: {', '.join(app_tags)}")
        logging.info(f"Category: {app_cat}")

        '''Click install button'''
        logging.info('Installing the application')
        install_button = app_controller.highlevel_query.find_by_classname(
            Widget.BUTTON, {"text": "Install"})
        if len(install_button) > 0:
            install_button[0].click()
            '''Wait until the app is installed'''
            installed = False
            while not installed:
                app_controller.delay(6)
                installed = len(app_controller.highlevel_query.find_by_classname(
                    Widget.BUTTON, {"text": "Uninstall"})) > 0
            logging.info('Installed successfully')
        else:
            paid_button = app_controller.highlevel_query.find_by_classname(Widget.BUTTON, {"text": re.compile("\d+\.\d+")})
            if len(paid_button) > 0:
                raise PaidAppError
            logging.warn(
                "Could not find the install button. The app may be already installed, skipping.")

        time.sleep(1)
        del app_controller
        time.sleep(8)

        return app_name, dev_name, app_cat

    def test(self, apk_path, action_count=10, install=True, debug=False, activity=None, install_type="apk", dump_apk=True, dump_manifest=True, proxy=True, reset_state=True):
        if not self.device_controller.is_online():
            raise DeviceOfflineError

        self.device_controller.set_wifi_proxy()

        '''Install the application'''
        if install:
            if install_type == "apk":
                self.device_controller.install_apk(apk_path)
            elif install_type == "playstore":
                app_name, dev_name, app_cat = self.install_via_playstore(apk_path)

                if app_cat == 'games':
                    raise GamesNotSupportedError

                '''Dump apk'''
                if dump_apk:
                    try:
                        self.device_controller.dump_apk(apk_path, f"apk/{apk_path}.apk")
                    except:
                        raise NotSupportedError

                    if dump_manifest:
                        manifest = self.device_controller.dump_apk_manifest(apk_path)
                        manifest["developer"] = dev_name
                        manifest["category"] = app_cat

                        if not activity:
                            activity = manifest["launchableActivity"]

                        with open(f"app_info/{apk_path}.json", "w") as app_info:
                            json.dump(manifest, app_info)

            else:
                raise Exception('Invalid installation type')


        '''Include app or appPackage into desired cap'''
        extended_desired_cap = self.desired_cap
        if '.apk' in apk_path:
            '''Install with apk'''
            package_name = os.path.splitext(os.path.basename(apk_path))[0]
            extended_desired_cap["app"] = apk_path
        else:
            package_name = apk_path
            '''To launch an app without reinstall, defautlt activity name is required'''
            if not activity:
                activity = self.device_controller.get_default_activity_of(
                    package_name)
                
                if not activity:
                    raise Exception(
                        "Could not find the default activity of the application.")
                        
            logging.info(
                    f"The application will be started with the activity {activity}")


        '''Initialize a proxy server'''
        if proxy:
            proxy_port = self.desired_cap['proxyPort']
            logging.info(f"Setting wifi proxy to {self.proxy_host}:{proxy_port}")
            self.device_controller.set_wifi_proxy(self.proxy_host, proxy_port)
            proxy_controller = ProxyController(proxy_port, package_name)

        app_controller = AppController(
            extended_desired_cap, package_name, activity)

        self.on_before(app_controller)

        if hasattr(self, 'action_count'):
            action_count = self.action_count

        if debug:
            self.__debug(app_controller)
        else:
            for i in progressbar(range(action_count)):
                self.on_perform(app_controller, i)
                time.sleep(1)

        '''Cleaning up'''
        logging.info('Cleaning up')
        if proxy:
            self.device_controller.set_wifi_proxy()  # Set back to default
        if reset_state:
            logging.info('Uninstalling the application')
            self.device_controller.uninstall(package_name)
            logging.info('Rebooting the device')
            self.device_controller.reboot()

        logging.info('The application has been tested sucessfully')


