from subprocess import Popen, PIPE
import os
import time
import logging
import zipfile
import json
import re

adb_path = "adb"


class DeviceController:
    def __init__(self, device_name):
        self.device_name = device_name
        if '.' in device_name:
            # Connect tcp when device_name is in IP address format.
            cmd = f"adb connect {device_name}"
            os.system(cmd)

    def __extract_online_devices(self):
        """Extract online devices using adb"""
        p = Popen([adb_path, "devices"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate()
        rc = p.returncode
        output = output.decode("utf-8")
        online_devices = []
        for line in output.strip().split("\n")[1:]:
            id, type = line.split()
            if type == "device":
                online_devices.append(id)
        return online_devices

    def __adb_shell_input(self, *commands):
        """Execute adb shell input command(s) sequentially"""
        cmd = '&&'.join(
            [f"{adb_path} -s {self.device_name} shell input ${cmd}" for cmd in commands])
        os.system(cmd)

    def __adb_reboot(self):
        """Reboot the device via adb shell"""
        cmd = f"{adb_path} -s {self.device_name} reboot"
        os.system(cmd)

    def __adb_install(self, apk_path):
        """Install apk into the device"""
        cmd = f"{adb_path} -s {self.device_name} install -r {apk_path}"
        os.system(cmd)

    def __adb_shell(self, *commands):
        cmd = f"{adb_path} -s {self.device_name} shell {' '.join(commands)}"
        os.system(cmd)

    def __execute_and_get_output(self, cmd):
        """Run command and get output from stdout"""
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate()
        rc = p.returncode
        return output.decode("utf-8").strip()

    def is_online(self):
        for device in self.__extract_online_devices():
            if self.device_name in device:
                return True
        return False

    def wait_until_online(self, interval=2):
        online = False
        while not online:
            online = self.is_online()
            time.sleep(interval)

    def unlock(self):
        swipe_input = "360 1600 360 1000 100"

        self.__adb_shell_input(
            "keyevent KEYCODE_WAKEUP",
            "keyevent 26",
            "keyevent 26"
        )

        time.sleep(3)

        self.__adb_shell_input(
            f"swipe {swipe_input}",
            "text 1234",
            "keyevent 66",
            "keyevent KEYCODE_BACK"
        )

    def reboot(self):
        """Reboot and do some necessary things"""
        self.__adb_reboot()
        self.wait_until_online()
        time.sleep(10)
        self.unlock()

    def install_apk(self, apk_path):
        self.__adb_install(apk_path)

    def get_default_activity_of(self, package_name):
        cmd = [adb_path, "-s", self.device_name, "shell", "cmd", "package",
               "resolve-activity", "--brief", package_name, "| tail -n 1"]
        return self.__execute_and_get_output(cmd).replace('/', '')

    """If host and proxy_port are not provided, proxy setting will be removed instead."""

    def set_wifi_proxy(self, host='', proxy_port='0'):
        cmd = f"adb -s {self.device_name} shell settings put global http_proxy {host}:{proxy_port}"
        os.system(cmd)

    def dump_apk(self, package_name, file_path):
        # Get apk path
        apk_path_list = self.__execute_and_get_output(
            [adb_path, "-s", self.device_name, "shell", "pm", "path", package_name])

        """Sample output of apk_path_list:
            package:/data/app/com.ookbee.ookbeecomics.android-1/base.apk
        """
        base_apk_path = (apk_path_list.split()[0].strip())[8:]

        logging.info(f"Dumping the apk from {base_apk_path} to {file_path}")

        # Move to temp folder
        TEMP_APK_DIR = '/storage/emulated/0/Download/'
        temp_apk_path = TEMP_APK_DIR + package_name + '.apk'
        self.__adb_shell("cp", base_apk_path, temp_apk_path)

        # Dump apk
        cmd = f"{adb_path} pull {temp_apk_path} {file_path}"
        os.system(cmd)

        self.__adb_shell("rm", temp_apk_path)

    def dump_apk_manifest(self, package_name):
        apk_path = f"apk/{package_name}.apk"
        cmd = ["aapt", "dump", "badging", apk_path]
        out = self.__execute_and_get_output(cmd)

        versionName = None
        appLabel = None
        appIcon = None
        launchableActivity = None

        for line in out.split('\n'):
            line = line.strip()
            if not versionName and 'versionName=' in line:
                version_search = re.search("versionName=\'(.*?)\'", line)
                if version_search:
                    versionName = version_search.group(1)
            elif not appLabel and 'application-label:' in line:
                app_label_search = re.search(
                    "application-label.*?:\'(.*?)\'", line)
                if app_label_search:
                    appLabel = app_label_search.group(1)
            elif not appIcon and 'application-icon' in line:
                app_icon_search = re.search(
                    "application-icon-640:\'(.*?)\'", line)
                if app_icon_search:
                    appIcon = app_icon_search.group(1)
            elif not launchableActivity and 'launchable-activity' in line:
                app_activity_search = re.search(
                    "launchable-activity: name=\'(.*?)\'", line)
                if app_activity_search:
                    launchableActivity = app_activity_search.group(1)

        '''Dump app icon'''
        with zipfile.ZipFile(apk_path) as bundle:
            with bundle.open(appIcon) as icon_image:
                with open(f"app_icons/{package_name}.png", 'wb') as icon_file:
                    icon_file.write(icon_image.read())

        result = {
            "versionName": versionName,
            "appLabel": appLabel,
            "appIcon": appIcon,
            "launchableActivity": launchableActivity,
        }

        logging.info(f"Extracted the manifest from the apk. Got {result}")

        return result
