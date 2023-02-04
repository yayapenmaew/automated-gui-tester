# Automated Android Application Tester Framework

A framework for developing automated Android application GUI tester.

## Requirements

- python3
- `pip3 install -r requirements.txt`
- adb (Included in Android SDK Platform-Tools)
- aapt
- acvtool (for benchmarking only) [[Installation](https://github.com/pilgun/acvtool)]

Please make sure that `adb` and `aapt` can be executed from command line.

## Installation

### Environment variables

Copy `.env.example` and rename it to `.env`. Fill all required variables.
Change `MITM_PATH` which matchs the operating system. For example:

```
MITM_PATH=./tester/mitmproxy/osx/mitmdump
ANDROID_SDK_ROOT=/Users/<user>/Library/Android/sdk
JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-13.0.1.jdk/Contents/Home
```

### Device's PI

Copy `analyzer/PI.example.json` and rename it to `analyzer/PI.json`. Fill the device's information.

## Running the example script

To perform a dynamic testing, run

```
python3 main.py <device_name> <app_id> <proxy_host>
python3 main.py emulator-5554 com.miga.mytown 192.168.10.167 --appium_port 8201
python3 main.py emulator-5554 com.facebook.katana 192.168.10.206 --appium_port 8201
python3 main.py Pixel_3a_API_33_arm64-v8a com.cbs.app 192.168.1.249
python3 main.py 10.0.2.15 com.cbs.app 127.0.0.1
python3 main.py sdk_gphone64_arm64 com.cbs.app 192.168.1.249
```

Optional arguments can be specified by `--<name> <value>` flag. Run python3 main.py -h for more information about the arguments.

The script’s arguments are described below:

| Argument       | Description                                                                                                                                                   |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| device_name    | Device UDID or IP address [Required]                                                                                                                          |
| app_id         | Application identifier [Required]                                                                                                                             |
| proxy_host     | Proxy host [Required]                                                                                                                                         |
| version        | Android version [Default `7.0`]                                                                                                                               |
| proxy_port     | Proxy port [Default `8080`]                                                                                                                                   |
| system_port    | System port [Default `820`]                                                                                                                                   |
| appium_port    | Appium port [Default `4723`]                                                                                                                                  |
| timeout        | Timeout (second) [Default `900`]                                                                                                                              |
| mode           | Test mode (monkey, ga). [Default `ga`]                                                                                                                        |
| endpoint       | Endpoint at which the result will be sent. If not specified, the JSON result will be shown on stdout [Default `None`]                                         |
| uuid           | Uuid which will be forwarded to the track manager. If not specified, no `uuid` will be sent. [Default `None`]                                                 |
| latest_version | Latest version of the application. The script will terminate with an error code if the downloaded app has the same version as latest_version [Default `None`] |
| force          | Ignore latest_version checking and force the script to test                                                                                                   |

## Writing a simple tester

You can simulate random interactions like Monkey does with a few lines of code.

Connect a testing device into the computer, change `device_udid` and `android_version` then run the script below.

```python
from tester.application import DynamicTestingApplication
from tester.app_controller import AppController

device_udid = "0123456789ABCDEF"
android_version = "7.0"
proxy_host = "192.168.1.249"

app = DynamicTestingApplication(device_udid, android_version, proxy_host)

def on_perform(app_controller: AppController):
    app_controller.random_touch()

app.set_action_count(30)
app.foreach(on_perform)

app.test('com.zhiliaoapp.musically.go')
```
