class AndroidDesiredCapabilities:
    def generate(udid, version, system_port, proxy_port, appium_port):
        return {
            "deviceName": udid,
            "platformName": "Android",
            "udid": udid,
            "version": version,
            # "app": "##apk_path##",
            "autoGrantPermissions": True,
            "androidInstallTimeout": 90000,
            "uiautomator2ServerInstallTimeout": 90000,
            "uiautomator2ServerLaunchTimeout": 90000,
            "adbExecTimeout": 90000,
            "clearSystemFiles": True,
            "proxyPort": proxy_port,
            "systemPort": system_port,
            "appiumPort": appium_port,
            'fullReset': False,
            'unicodeKeyboard': True,
            'resetKeyboard': True,
            'isHeadless': False,
        }
