import os
from os import path
import time
import random
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from .highlevel_query import HighlevelQuery


class AppController:
    def __init__(self, desired_cap, apk_path, activity=None):
        self.desired_cap = desired_cap
        self.appium_port = desired_cap['appiumPort']
        self.package_name = path.splitext(path.basename(apk_path))[0]
        self.desired_cap['appPackage'] = self.package_name
        if activity:
            self.desired_cap['appActivity'] = activity

        self.__start_appium()
        time.sleep(2)
        self.connect_driver()
        self.launch_app()
        time.sleep(5)
        self.package_name = self.get_current_package()

        self.highlevel_query = HighlevelQuery(self.driver)

        print(self.package_name)

    def __del__(self):
        self.__kill_appium()

    def __start_appium(self):
        cmd = f"appium -p {self.appium_port} >> log/{self.package_name}.log &"
        os.system(cmd)

    def __kill_appium(self):
        cmd = f"pkill -f 'appium -p {self.appium_port}'"
        os.system(cmd)

    def connect_driver(self):
        """Reconnect appium web driver"""
        self.driver = webdriver.Remote(
            f"http://0.0.0.0:{self.appium_port}/wd/hub", self.desired_cap)

    def get_window_size(self):
        window_size = self.driver.get_window_size()
        return window_size['width'], window_size['height']

    def get_current_package(self):
        return self.driver.current_package

    def get_current_activity(self):
        return self.driver.current_activity

    def is_on_current_package(self):
        """Return whether current screen is come from the running application or not"""
        return self.get_current_package() == self.package_name

    def get_clickable_elements(self):
        return self.driver.find_elements_by_android_uiautomator("new UiSelector().clickable(true)")

    def launch_app(self):
        self.driver.launch_app()

    def random_touch(self):
        width, height = self.get_window_size()

        x_percent = random.randrange(100)
        y_percent = random.randrange(100)

        x, y = width * x_percent / 100, height * y_percent / 100

        TouchAction(self.driver).press(x=x, y=max(100, y)).perform()

    def swipe(self, dir='left', duration=400):
        assert dir in ['left', 'right', 'down', 'up']
        width, height = self.get_window_size()
        if dir == 'down':
            try:
                self.driver.swipe(width/2, height/2, width/2, height/4, duration)
            except:
                self.driver.swipe(height/2, width/2, height/2, width/4, duration)
        elif dir == 'up':
            try:
                self.driver.swipe(width/2, height/2, width/2, height*3/4, duration)
            except:
                self.driver.swipe(height/2, width/2, height/2, width*3/4, duration)		
        elif dir == 'right':
            try:
                self.driver.swipe(width/2, height/2, width*3/4, height/2, duration)
            except:
                self.driver.swipe(height/2, width/2, height/4, width/4, duration)
        elif dir == 'left':
            try:
                self.driver.swipe(width*3/4, height/2, width/2, height/2, duration)
            except:
                self.driver.swipe(height/2, width/2, height*3/4, width/4, duration)

    def delay(self, duration=1):
        time.sleep(duration)

    def back(self):
        self.driver.back()

    def get_page_source(self):
        return self.driver.page_source
