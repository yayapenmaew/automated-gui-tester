#!/usr/bin/env python3
from tester.application import DynamicTestingApplication
from tester.app_controller import AppController
from tester.rules.rules import initialize_rules

app = DynamicTestingApplication("K6T6R17909001485", "7.0")

app.set_env_path(
    android_sdk_root="/Users/nisaruj/Library/Android/sdk",
    java_home="/Library/Java/JavaVirtualMachines/jdk-13.0.1.jdk/Contents/Home"
)

rules = initialize_rules()

def on_perform(app_controller: AppController):
    for rule in rules:
        if rule.match(app_controller):
            rule.action(app_controller)

app.set_action_count(100)
app.set_on_perform(on_perform)

app.test(
    './com.android.deskclock.apk', 
    install=False,
    # debug=True,
    activity="com.android.deskclock.AlarmsMainActivity"
)