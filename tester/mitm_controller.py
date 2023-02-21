import logging
import os
import subprocess
import psutil
import signal
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class ProxyController:
    def __init__(self, proxy_port=8080, package_name="untitled", device_name="", mitm_path=os.environ.get("MITM_PATH")):
        self.proxy_port = proxy_port
        self.package_name = package_name
        self.device_name = device_name
        self.mitm_path = mitm_path
        self.log_file = open(f"./log_mitm/{self.package_name}.log", "w")
        os.system("pkill -f 'mitmdump -p '")
        self.__start_mitmproxy()
        logging.info(f"Initializing mitmproxy at port {self.proxy_port}")

    def __start_mitmproxy(self):
        logging.info(f"hardump=result-{self.device_name}/{self.package_name}.har")
        cmd = [self.mitm_path, "-p", str(self.proxy_port), "-s", "./tester/mitmproxy/har_dump.py",
               "--set", f"hardump=result-{self.device_name}/{self.package_name}.har"]
        self.mitm = subprocess.Popen(
            cmd, stdout=self.log_file, preexec_fn=os.setsid)

    def __kill_mitmproxy(self):
        os.killpg(os.getpgid(self.mitm.pid), signal.SIGTERM)

    def __del__(self):
        self.__kill_mitmproxy()
        self.log_file.close()
        logging.info("Mitmproxy exited peacefully")
