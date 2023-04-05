import json
import os
from dbMethods import storeSuccessToDB, storeToTestFailDB
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
from .exceptions import AlreadyTestedError, AppNotFoundError, DeviceOfflineError, DownloadError, GamesNotSupportedError, InstallButtonError, NotSupportedError, PaidAppError
from .playstore_helper import get_cat_slug
from google_play_scraper import app as google_play_scraper_app


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
        os.system(f"mkdir result-{self.device_udid}")
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

        APP_NAME = google_play_scraper_app(package_name,lang='en', country='us')['title']
        logging.info(f"Installing APP_NAME {APP_NAME} via Playstore")

        '''Handle Server Error'''
        tryagain_button = app_controller.highlevel_query.find_by_classname(
            Widget.BUTTON, {"text": "Try again"})
        if(len(tryagain_button)>0):
            tryagain_button[0].click()


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
        #search_bar.send_keys(package_name)
        search_bar.send_keys(APP_NAME)

        '''Click enter to search'''
        ENTER_KEYCODE = 66
        app_controller.send_key_event(ENTER_KEYCODE)
        app_controller.delay(3)

        '''Click the first search result which is not an Ads'''
        results = []
        resname = []
        start_time = time.time()
        seconds = 12
        while not results:
            results = app_controller.highlevel_query.find_by_classname(
                Widget.LINEAR_LAYOUT, {"clickable": True})
            logging.info(f"results {results}")
            logging.info(f"len results {len(results)}")

            no_result = len(app_controller.highlevel_query.find_by_classname(
                Widget.TEXT_VIEW, {"text": re.compile("No results for")})) > 0
            if no_result:
                raise AppNotFoundError(appId=package_name, device=self.device_udid)

            app_controller.delay(3)
            current_time = time.time()
            elapsed_time = current_time - start_time
            if elapsed_time > seconds:
                break

        if not results:
            app_list = app_controller.highlevel_query.find_by_classname(
                Widget.VIEW)
            resname = app_controller.highlevel_query.find_by_classname(
            Widget.TEXT_VIEW, {"text": APP_NAME })
            if len(resname)>1:
                resname[0].click()
            else:
                app_list = app_controller.highlevel_query.find_by_classname(
                Widget.VIEW)
                if len(app_list)>0:
                    countA = 0
                    for app in app_list:
                        app_detail = app.get_attribute('contentDescription')
                        if app_detail:
                            curr_app_name = app_detail.split("\n")[0].replace("App: ","")
                            isTargetApp = curr_app_name == APP_NAME
                            if isTargetApp:
                                app_list[countA].click()
                                break
                        countA += 1
        else:
            '''Skip advertisement and suggestion results'''
            app_list = app_controller.highlevel_query.find_by_classname(
                Widget.VIEW)
            result_offset = 0
            countNoDetail = 0
            for app in app_list:
                app_detail = app.get_attribute('contentDescription')
                if app_detail:
                    curr_app_name = app_detail.split("\n")[0].replace("App: ","")
                    isTargetApp = curr_app_name == APP_NAME
                    if isTargetApp:
                        break
                    result_offset += 1
                else:
                    countNoDetail += 1

            result_offset += len(app_controller.highlevel_query.find_by_classname(
                Widget.TEXT_VIEW, {"text": "Did you mean:"}))
            #logging.info(f'146 {results}')
            #logging.info(f'147 {result_offset}')
            logging.info(f'result_offset = {result_offset}')
            if countNoDetail != len(app_list): #else all are none --> just click install if have, if do not have --> cannot download
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

        '''Click Got it button'''
        gotit_button = app_controller.highlevel_query.find_by_classname(
            Widget.BUTTON, {"text": "Got it"})
        if len(gotit_button) > 0:
            gotit_button[0].click()
            app_info = app_controller.highlevel_query.find_by_classname(
            Widget.TEXT_VIEW)[:2]
            app_name, dev_name = list(
                map(lambda elem: elem.get_attribute('text'), app_info))
            logging.info(f"2 here {app_name} ({dev_name})")
            if app_name != 'How ratings are calculated' and app_name != APP_NAME:
                err = 'cannot find the application'
                logging.info(f"{app_name} is not {APP_NAME}")
                raise AppNotFoundError(appId=package_name, device=self.device_udid)

        '''Handle complete account setup'''
        cpas_widget = app_controller.highlevel_query.find_by_classname(
            Widget.TEXT_VIEW, {"text": "Complete account setup"})
        if len(cpas_widget)>0:
            logging.info('Complete Account Setup 1')
            cont_button = app_controller.highlevel_query.find_by_classname(
            Widget.BUTTON, {"text": "Continue"})
            if(len(cont_button)>0):
                cont_button[0].click()
                logging.info('Click continue 1')
                skip_button = app_controller.highlevel_query.find_by_classname(
            Widget.BUTTON, {"text": "Skip"})
                if(len(skip_button)>0):
                    skip_button[0].click()
                    logging.info('Click skip 1')
        """ cont_button = app_controller.highlevel_query.find_by_classname(
            Widget.BUTTON, {"text": "Continue"})
        skip_button = app_controller.highlevel_query.find_by_classname(
            Widget.BUTTON, {"text": "Skip"})
        if(len(skip_button)>0):
            skip_button[0].click()
        else:
            if len(cont_button)>0: cont_button[0].click() """


        '''Click install button'''
        logging.info('Installing the application')
        #handle complete account setup widget
        continue_button3 = app_controller.highlevel_query.find_by_classname(Widget.BUTTON, {"text": "Continue"})
        skip_button3 = app_controller.highlevel_query.find_by_classname(Widget.BUTTON, {"text": "Skip"})
        if len(continue_button3) > 0:
            if len(skip_button3) > 0:
                skip_button3[0].click()
                logging.info('Click skip 3')
            else:
                continue_button3[0].click()
                logging.info('Click continue 3')
        if len(skip_button3) > 0:
            skip_button3[0].click()
            logging.info('Click skip 3.5')
        install_button = app_controller.highlevel_query.find_by_classname(
            Widget.BUTTON, {"text": "Install"})
        if len(install_button) > 0:
            install_button[0].click()
            if app_name != 'How ratings are calculated' and app_name != APP_NAME:
                err = 'cannot find the application'
                logging.info(f"{app_name} is not {APP_NAME}")
                raise AppNotFoundError(appId=package_name, device=self.device_udid)

            '''Grant permissions'''
            app_controller.delay(5)
            perm_accept_button = app_controller.highlevel_query.find_by_classname(
                Widget.BUTTON, {"text": "Accept"})
            if len(perm_accept_button) > 0:
                perm_accept_button[0].click()

            '''Wait until the app is installed'''
            installed = False
            while not installed:
                #handle complete account setup widget
                continue_button2 = app_controller.highlevel_query.find_by_classname(Widget.BUTTON, {"text": "Continue"})
                skip_button2 = app_controller.highlevel_query.find_by_classname(Widget.BUTTON, {"text": "Skip"})
                install_button = app_controller.highlevel_query.find_by_classname(Widget.BUTTON, {"text": "Install"})
                cantdownload_button = app_controller.highlevel_query.find_by_classname(Widget.TEXT_VIEW, {"text": "Can't download"})
                tapToProceed = app_controller.highlevel_query.find_by_classname(
            Widget.TEXT_VIEW, {"text": 'Tap to proceed' })
                if len(tapToProceed) > 0:
                    tapToProceed[0].click()
                if len(cantdownload_button)>0:
                    logging.info("Can't download")
                    raise DownloadError(appId=package_name, device=self.device_udid)
                if len(install_button) > 0:
                    install_button[0].click()
                if len(continue_button2) > 0:
                    if len(skip_button2) > 0:
                        skip_button2[0].click()
                        logging.info('Click skip 2')
                    else:
                        continue_button2[0].click()
                        logging.info('Click continue 2')

                installed = (len(app_controller.highlevel_query.find_by_classname(
                    Widget.BUTTON, {"text": "Uninstall"})) > 0 or len(app_controller.highlevel_query.find_by_classname(
                        Widget.BUTTON, {"text": "Open"})) > 0 or len(app_controller.highlevel_query.find_by_classname(
                        Widget.BUTTON, {"text": "Play"})) > 0) and not ((len(app_controller.highlevel_query.find_by_classname(
                        Widget.BUTTON, {"text": "Open"})) > 0 and len(app_controller.highlevel_query.find_by_classname(
                        Widget.BUTTON, {"text": "Cancel"})) > 0) or ((len(app_controller.highlevel_query.find_by_classname(
                        Widget.BUTTON, {"text": "Play"})) > 0 and len(app_controller.highlevel_query.find_by_classname(
                        Widget.BUTTON, {"text": "Cancel"})) > 0)))
                app_controller.delay(6)
            logging.info('Installed successfully')
            """ logging.info('Run Objection on the target application')
            os.system(f'objection -g {package_name} explore -q')
            os.system(f'android sslpinning disable') """
        else:
            paid_button = app_controller.highlevel_query.find_by_classname(
                Widget.BUTTON, {"text": re.compile("\d+\.\d+")})
            if len(paid_button) > 0:
                raise PaidAppError(appId=package_name, device=self.device_udid)
            logging.warn(
                "Could not find the install button. The app may be already installed, skipping.")
            raise InstallButtonError(appId=package_name, device=self.device_udid)

        time.sleep(1)
        del app_controller
        time.sleep(8)

        logging.info(f"1 here {app_name} ({dev_name})")
        return app_name, dev_name, app_cat

    def test(
            self,
            apk_path,
            action_count=20,
            install=True,
            debug=False,
            activity=None,
            install_type="apk",
            dump_apk=True,
            dump_manifest=True,
            proxy=True,
            reset_state=True,
            latest_version=None):
        if not self.device_controller.is_online():
            raise DeviceOfflineError(appId=apk_path, device=self.device_udid)

        self.device_controller.set_wifi_proxy()

        '''Install the application'''
        if install:
            if install_type == "apk":
                self.device_controller.install_apk(apk_path)
            elif install_type == "playstore":
                app_name, dev_name, app_cat = self.install_via_playstore(
                    apk_path)

                if app_cat == 'games':
                    raise GamesNotSupportedError(appId=apk_path, device=self.device_udid)

                '''Dump apk'''
                if dump_apk:
                    try:
                        self.device_controller.dump_apk(
                            apk_path, f"apk/{apk_path}.apk")
                    except:
                        raise NotSupportedError(appId=apk_path, device=self.device_udid)

                    if dump_manifest:
                        manifest = self.device_controller.dump_apk_manifest(
                            apk_path)
                        manifest["developer"] = dev_name
                        manifest["category"] = app_cat

                        if latest_version and latest_version == manifest["versionName"]:
                            raise AlreadyTestedError(appId=package_name, device=self.device_udid)

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
            storeSuccessToDB(package_name, self.device_udid)

        '''Initialize a proxy server'''
        if proxy:
            proxy_port = self.desired_cap['proxyPort']
            logging.info(
                f"Setting wifi proxy to {self.proxy_host}:{proxy_port}")
            self.device_controller.set_wifi_proxy(self.proxy_host, proxy_port)
            proxy_controller = ProxyController(proxy_port, package_name, device_name=self.device_udid)

        app_controller = AppController(
            extended_desired_cap, package_name, activity)

        self.on_before(app_controller)
        if hasattr(self, 'action_count'):
            action_count = self.action_count
            logging.info(
                f"Action count: {action_count}")

        if debug:
            self.__debug(app_controller)
        else:
            for i in progressbar(range(action_count)):
                self.on_perform(app_controller, i)
                # time.sleep(1)

        '''Cleaning up'''
        if proxy:
            del proxy_controller
        logging.info('Cleaning up')
        if proxy:
            self.device_controller.set_wifi_proxy()  # Set back to default
        if reset_state:
            logging.info('Uninstalling the application')
            self.device_controller.uninstall(package_name)
            # logging.info('Rebooting the device')
            # self.device_controller.reboot()

        logging.info('The application has been tested sucessfully')
