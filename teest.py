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
