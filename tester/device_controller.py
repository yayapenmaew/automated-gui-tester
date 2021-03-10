from subprocess import Popen, PIPE
import os
import time

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
        cmd = [adb_path, "shell", "cmd", "package", "resolve-activity", "--brief", package_name, "| tail -n 1"]
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate()
        rc = p.returncode
        output = output.decode("utf-8")
        return output.strip().replace('/', '')
