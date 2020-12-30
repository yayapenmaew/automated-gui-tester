from tester.application import DynamicTestingApplication
from tester.app_controller import AppController

app = DynamicTestingApplication("K6T6R17909001485", "7.0")

app.set_env_path(
    android_sdk_root="/Users/nisaruj/Library/Android/sdk",
    java_home="/Library/Java/JavaVirtualMachines/jdk-13.0.1.jdk/Contents/Home"
)

def on_perform(app_controller: AppController):
    app_controller.random_touch()

app.set_on_perform(on_perform)

app.test('./demo.apk')
