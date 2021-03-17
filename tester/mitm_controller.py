import logging
import os
import subprocess
import psutil
import signal


class ProxyController:
    def __init__(self, proxy_port=8080, package_name="untitled", mitm_path="./tester/mitmproxy/osx/mitmdump"):
        self.proxy_port = proxy_port
        self.package_name = package_name
        self.mitm_path = mitm_path
        self.log_file = open(f"./log_mitm/{self.package_name}.log", "w")
        self.__start_mitmproxy()
        logging.info(f"Initializing mitmproxy at port {self.proxy_port}")

    def __start_mitmproxy(self):
        cmd = [self.mitm_path, "-p", str(self.proxy_port), "-s", "./tester/mitmproxy/har_dump.py",
               "--set", f"hardump=result/{self.package_name}.har"]
        self.mitm = subprocess.Popen(
            cmd, stdout=self.log_file, preexec_fn=os.setsid)

    def __kill_mitmproxy(self):
        os.killpg(os.getpgid(self.mitm.pid), signal.SIGTERM)

    def __del__(self):
        self.__kill_mitmproxy()
        self.log_file.close()
        logging.info("Mitmproxy exited peacefully")
