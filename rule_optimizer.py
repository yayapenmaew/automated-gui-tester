#!/usr/bin/env python3
from tester.application import DynamicTestingApplication
from tester.app_controller import AppController
from tester.rules.rules import initialize_rules, BackToAppRule
from tester.rules.visual_state import VisualState, VisualStateGraph, ETVisualState
import threading
import time
import logging
import matplotlib.pyplot as plt
import logging
import argparse
import os
from tester.exceptions import DynamicTestError, PaidAppError
from dotenv import load_dotenv, find_dotenv
import sys
import random
from optimizer.ga_optimizer import BaseGeneticOptimizer
from benchmark.benchmark import COSMOBenchmark

class TesterConfig:
    DEVICE_NAME = "K6T6R17909001485"
    # DEVICE_NAME = "192.168.1.33:5555"
    PROXY_HOST = "192.168.1.249"
    ANDROID_VERSION = "7.0"
    N_ACTIONS = 50
    ALWAYS_INSTALL_APP = False
    APPLICATION = "org.secuso.privacyfriendlynetmonitor"
    SOURCE_PATH = "/Users/nisaruj/Desktop/COSMO/app_source/privacy-friendly-netmonitor"

class GeneticOptimizer(BaseGeneticOptimizer):
    def __init__(self, random_state=None, debug=False, app_id=TesterConfig.APPLICATION):
        rules = initialize_rules(exclude = ["BackToAppRule"])
        self.installed = False
        self.app_id = app_id

        super().__init__(rules, random_state, debug)

    def __append_result(self, app_name, rule, codecov_score=0, state_score=0, filename="ga_scores.txt"):
        with open(filename, "a") as fp:
            fp.write(app_name + "\t" + str(rule) + "\t" + str(codecov_score) + "\t" + str(state_score) + "\n")

    def fitness(self, agent):
        print(agent)
        selected_rules = [BackToAppRule()]
        for i in range(len(self.rules)):
            if agent[i]:
                selected_rules.append(self.rules[i])

        # codecov_score = run_benchmark(selected_rules, mode="coverage")
        try:
            state_score = run_benchmark(selected_rules, self.app_id, mode="state", install=(not self.installed))
        except Exception as e:
            print('Error:', str(e))
            state_score = -1
        self.installed = True
        # state_score, codecov_score = run_benchmark(selected_rules, mode="both")

        self.__append_result(self.app_id, agent, state_score=state_score, filename="ga_benchmark.txt")
        time.sleep(5)

        print('Score:', state_score)
        return state_score


def run_benchmark(rules, app_id, mode = "coverage", install=False):
    if mode == "coverage" or mode == "both":
        COSMOBenchmark.preparing_benchmark(app_id)

    app = DynamicTestingApplication(
            udid=TesterConfig.DEVICE_NAME,
            version=TesterConfig.ANDROID_VERSION,
            proxy_host=TesterConfig.PROXY_HOST,
            mitm_path=os.environ.get("MITM_PATH"),
        )

    '''In case Appium needs proper env paths'''
    app.set_env_path(
        android_sdk_root=os.environ.get("ANDROID_SDK_ROOT"),
        java_home=os.environ.get("JAVA_HOME")
    )

    app.set_action_count(TesterConfig.N_ACTIONS)

    if mode == "state" or mode == "both":
        states = VisualStateGraph()
    def on_perform(app_controller: AppController, step):
        
        if mode == "state" or mode == "both":
            current_state = VisualState(app_controller)
            states.add_transition(current_state)

        for rule in rules:
            try:
                if rule.match(app_controller):
                    # print(rule.name())
                    rule.action(app_controller)
            except KeyboardInterrupt:
                return
            except:
                pass
                # logging.error('Rule', rule.name(),
                #                 'error, try to posepone...')

    app.foreach(on_perform)

    app.test(
        app_id,
        install_type='playstore',
        install=install,
        proxy=False,
        reset_state=False
    )

    if mode == "state":
        return len(states.nodes())
    elif mode == "coverage":
        code_cov, detailed_cov = COSMOBenchmark.generate_report(app_id, TesterConfig.SOURCE_PATH)
        return code_cov
    elif mode == "both":
        code_cov, detailed_cov = COSMOBenchmark.generate_report(app_id, TesterConfig.SOURCE_PATH)
        return len(states.nodes()), code_cov

if __name__ == '__main__':
    app_list = sys.argv[1]
    with open(app_list, 'r') as fp:
        for line in fp:
            app_id = line.strip()
            if '%' in app_id:
                continue
            try:
                optimizer = GeneticOptimizer(debug=True, app_id=app_id)
                optimizer.optimize(n_gen=3, pop_size=4, n_parents=2)
            except KeyboardInterrupt:
                print('Terminating ...')
                break
