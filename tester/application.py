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


class DynamicTestingApplication:
    def __init__(
        self,
        udid,
        version,
        proxy_host,
        system_port=8200,
        proxy_port=8080,
        appium_port=4723,
        mitm_path="./tester/mitmproxy/osx/mitmdump"
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
        search_box = app_controller.highlevel_query.find_by_classname(Widget.TEXT_VIEW, {
            "text": re.compile("Search", re.IGNORECASE)
        })[0]
        search_box.click()
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
        '''Skip advertisement results'''
        ads_result_count = len(app_controller.highlevel_query.find_by_classname(
            Widget.VIEW, {"contentDescription": re.compile("\nAd\n")}))
        results[ads_result_count].click()

        app_controller.delay(3)

        '''Retrieve app information'''
        logging.info('Retrieving app info')
        app_info = app_controller.highlevel_query.find_by_classname(
            Widget.TEXT_VIEW)[:2]
        app_name, dev_name = list(
            map(lambda elem: elem.get_attribute('text'), app_info))
        logging.info(f"{app_name} ({dev_name})")

        '''DEPRECATED'''
        '''Get app icon by taking a screenshot'''
        # app_icon = app_controller.highlevel_query.find_by_classname(Widget.IMAGE_VIEW)[
        #     0]
        # icon_location = app_icon.location_in_view
        # icon_bounds = ((icon_location['x'], icon_location['y']), (icon_location['x'] +
        #                                                           app_icon.size['width'], icon_location['y'] + app_icon.size['height']))
        # icon_file = BytesIO(base64.b64decode(app_controller.get_screenshot()))
        # icon_img = Image.open(icon_file)
        # icon_img = icon_img.crop(
        #     (icon_bounds[0][0], icon_bounds[1][0], icon_bounds[0][1], icon_bounds[1][1]))

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
            logging.warn(
                "Could not find the install button. The app may be already installed, skipping.")

        time.sleep(1)
        del app_controller
        time.sleep(8)

    def test(self, apk_path, action_count=10, install=True, debug=False, activity=None, install_type="apk"):
        if not self.device_controller.is_online():
            raise Exception('The testing device is offine')

        '''Install the application'''
        if install:
            if install_type == "apk":
                self.device_controller.install_apk(apk_path)
            elif install_type == "playstore":
                self.install_via_playstore(apk_path)
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
                logging.info(
                    f"The application will be started with the activity {activity}")
                if not activity:
                    raise Exception(
                        "Could not find the default activity of the application.")

        '''Initialize a proxy server'''
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
        self.device_controller.set_wifi_proxy()  # Set back to default

        logging.info('The application has been tested sucessfully')


