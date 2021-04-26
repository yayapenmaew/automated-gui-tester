import os
import sys
import time
import subprocess
import re

acvtool = "/Users/nisaruj/Desktop/acvtool/acvtool.py"
acvtool_wd = "/Users/nisaruj/acvtool/acvtool_working_dir"
RESULT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), './result'))


class ACVBenchmark:

    def start_instrumenting(app_id):
        p = subprocess.Popen([acvtool, "start", "-q", app_id])
        p.wait()

    def stop_instrumenting(app_id, report=True):
        p = subprocess.Popen([acvtool, "stop", app_id])
        p.wait()
        if report:
            ACVBenchmark.__generate_report(app_id)

            time.sleep(3)  # Wait for result file writing

            acv_helper = ACVToolHelper(
                f"{acvtool_wd}/report/{app_id}/report/index.html")
            return acv_helper.detailed_code_cov()
        return None

    def __generate_report(app_id):
        p = subprocess.Popen(
            [acvtool, "report", app_id, "-p", f"{acvtool_wd}/metadata/{app_id}.pickle"])
        p.wait()

    def benchmark(app_id):
        os.system(
            f"mkdir {os.path.join(os.path.dirname(__file__), './result')}")

        ACVBenchmark.start_instrumenting(app_id)
        print("Benchmarking...")

        time.sleep(10)

        code_cov, detailed_cov = ACVBenchmark.stop_instrumenting(app_id)
        print("Finished")
        print('Code coverage:', code_cov)
        print('Coverage detail:', detailed_cov)


class COSMOBenchmark:
    def preparing_benchmark(app_id):
        os.system(f"adb shell pm clear {app_id}")

    def __stop_coverage(app_id):
        p = subprocess.Popen(["adb", "shell", "am", "broadcast", "-p", app_id, "-a", "intent.END_COVERAGE"])
        p.wait()
        time.sleep(1)

        os.system(
            f"adb pull /sdcard/Android/data/{app_id}/files/coverage.ec {RESULT_DIR}")
        time.sleep(1)

    def generate_report(app_id, source_path):
        COSMOBenchmark.__stop_coverage(app_id)

        escape_result_dir = re.escape(RESULT_DIR).replace('/', '\\/')
        os.system(
            f"sed -i -E 's/dir: \".*\"/dir: \"{escape_result_dir}\"/g' {source_path}/app/jacoco-instrumenter-coverage.gradle")

        p = subprocess.Popen(
            [f"cd {source_path} && ./gradlew jacocoInstrumenterReport"], shell=True)
        p.wait()

        result_parser = HTMLResultParser(
            f"{source_path}/app/build/reports/jacoco/jacocoInstrumenterReport/html/index.html")
        return result_parser.detailed_code_cov()

    def benchmark(app_id, source_path):
        os.system(f"mkdir {RESULT_DIR}")

        COSMOBenchmark.preparing_benchmark(app_id)
        
        print('Starting benchmark')
        time.sleep(10)
        print('Generating report')

        code_cov, detailed_cov = COSMOBenchmark.generate_report(
            app_id, source_path)
            
        return code_cov, detailed_cov


if __name__ == '__main__':
    from helper import HTMLResultParser
    app_id = sys.argv[1]
    source_path = sys.argv[2]
    print(COSMOBenchmark.benchmark(app_id, source_path))
else:
    from .helper import HTMLResultParser
