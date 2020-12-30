# Automated Android Application Tester Framework

A framework for developing automated Android application GUI tester.

## Requirements

- Appium-Python-Client==1.0.2
- adb (Included in Android SDK Platform-Tools)

## Example
You can simulate random interactions like Monkey does with a few lines of code.

Connect a testing device into the computer, change `device_udid` and `android_version` then run the script below.

```python
from tester.application import DynamicTestingApplication
from tester.app_controller import AppController

device_udid = "0123456789ABCDEF"
android_version = "7.0"

app = DynamicTestingApplication(device_udid, android_version)

def on_perform(app_controller: AppController):
    app_controller.random_touch()

app.set_on_perform(on_perform)

app.test('./demo.apk')
```