#!/usr/bin/env python3
from tester.application import DynamicTestingApplication
from tester.app_controller import AppController
import time
import logging

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)

# app = DynamicTestingApplication("192.168.1.41:5555", "7.0")
app = DynamicTestingApplication(
    "K6T6R17909001485",
    "7.0",
    proxy_host="192.168.1.249",
    mitm_path="./tester/mitmproxy/osx/mitmdump"
)

'''In case Appium needs proper env paths'''
app.set_env_path(
    android_sdk_root="/Users/nisaruj/Library/Android/sdk",
    java_home="/Library/Java/JavaVirtualMachines/jdk-13.0.1.jdk/Contents/Home"
)

action_count = 20
app.set_action_count(action_count)

def on_perform(app_controller: AppController, step):
    try:
        app_controller.random_touch()
        app_controller.click_random_elements()
    except:
        pass

app.foreach(on_perform)

app.test(
    'com.ookbee.ookbeecomics.android',
    install_type='playstore',
    install=False
)