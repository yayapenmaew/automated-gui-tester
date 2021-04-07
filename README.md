# Automated Android Application Tester Framework (AAATF)

A framework for developing automated Android application GUI tester.

## Requirements

- python3
- `pip install -r requirements.txt`
- adb (Included in Android SDK Platform-Tools)
- aapt
- acvtool (for benchmarking only) [[Installation](https://github.com/pilgun/acvtool)]

Please make sure that `adb` and `aapt` can be executed from command line.

## Running the example script

```python
python main.py <device_id> com.ookbee.ookbeecomics.android <proxy_port>
```

Run `python main.py -h` for more argument information.

## Writing a simple tester
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