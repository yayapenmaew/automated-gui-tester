#!/usr/bin/env python3
from tester.application import DynamicTestingApplication
from tester.app_controller import AppController
from tester.rules.rules import initialize_rules
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
    PROXY_HOST = "192.168.1.249"
    ANDROID_VERSION = "7.0"
    N_ACTIONS = 10
    ALWAYS_INSTALL_APP = False
    APPLICATION = "protect.budgetwatch"
    SOURCE_PATH = "/Users/nisaruj/Desktop/COSMO/budget-watch"

class GeneticOptimizer(BaseGeneticOptimizer):
    def __init__(self, random_state=None, debug=False):
        rules = initialize_rules()

        super().__init__(rules, random_state, debug)

    def fitness(self, agent):
        print(agent)
        selected_rules = []
        for i in range(len(self.rules)):
            if agent[i]:
                selected_rules.append(self.rules[i])
        score = run_benchmark(selected_rules)
        print('Score:', score)
        return score


def run_benchmark(rules):
    COSMOBenchmark.preparing_benchmark(TesterConfig.APPLICATION)

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

    # states = VisualStateGraph()
    def on_perform(app_controller: AppController, step):
        
        # current_state = VisualState(app_controller)
        # states.add_transition(current_state)

        for rule in rules:
            try:
                if rule.match(app_controller):
                    # print(rule.name())
                    rule.action(app_controller)
            except KeyboardInterrupt:
                return
            except:
                logging.error('Rule', rule.name(),
                                'error, try to posepone...')

    app.foreach(on_perform)

    app.test(
        TesterConfig.APPLICATION,
        install_type='playstore',
        install=TesterConfig.ALWAYS_INSTALL_APP
    )

    # return len(states.nodes())

    code_cov, detailed_cov = COSMOBenchmark.generate_report(TesterConfig.APPLICATION, TesterConfig.SOURCE_PATH)
    return code_cov

if __name__ == '__main__':
    # print('# of states:', run_benchmark(initialize_rules()))
    optimizer = GeneticOptimizer(debug=True)
    optimizer.optimize(n_gen=1, pop_size=4, n_parents=2)
