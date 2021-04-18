import os
import sys
import time
import subprocess
from helper import ACVToolHelper

acvtool = "/Users/nisaruj/Desktop/acvtool/acvtool.py"
acvtool_wd = "/Users/nisaruj/acvtool/acvtool_working_dir"


class ACVBenchmark:

    def __start_instrumenting():
        p = subprocess.Popen([acvtool, "start", "-q", app_id])
        p.wait()

    def __stop_instrumenting():
        p = subprocess.Popen([acvtool, "stop", app_id])
        p.wait()

    def __generate_report():
        p = subprocess.Popen(
            [acvtool, "report", app_id, "-p", f"{acvtool_wd}/metadata/{app_id}.pickle"])
        p.wait()

    def benchmark(app_id):
        os.system(f"mkdir {os.path.join(os.path.dirname(__file__), './result')}")

        ACVBenchmark.__start_instrumenting()
        print("Benchmarking...")

        time.sleep(10)

        ACVBenchmark.__stop_instrumenting()
        print("Finished")

        time.sleep(3)

        ACVBenchmark.__generate_report()

        acv_helper = ACVToolHelper(f"{acvtool_wd}/report/{app_id}/report/index.html")
        print(acv_helper.detailed_code_cov())


if __name__ == '__main__':
    app_id = sys.argv[1]
    ACVBenchmark.benchmark(app_id)
