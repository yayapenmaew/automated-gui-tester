#!/usr/bin/env python3
from tester.application import DynamicTestingApplication
from tester.app_controller import AppController
from tester.rules.rules import initialize_rules
from tester.rules.visual_state import VisualState, VisualStateGraph, ETVisualState
from collections import defaultdict
import threading
import time
import logging
import matplotlib.pyplot as plt

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)

# app = DynamicTestingApplication("K6T6R17909001485", "7.0") # Connect by device's ID
app = DynamicTestingApplication("192.168.1.41:5555", "7.0") # Connect by IP address

app.set_env_path(
    android_sdk_root="/Users/nisaruj/Library/Android/sdk",
    java_home="/Library/Java/JavaVirtualMachines/jdk-13.0.1.jdk/Contents/Home"
)

rules = initialize_rules()
states = VisualStateGraph()

STATE_DEBUG_MODE = False

def on_perform(app_controller: AppController, step):
    if STATE_DEBUG_MODE:
        logging.debug(f"Step {step}")
        print('Fetching state')
        current_state = VisualState(app_controller)
        print('Fetched state')
        states.add_transition(current_state)
        print(states.nodes())
        states.show()
        time.sleep(1)

    for rule in rules:
        try:
            if rule.match(app_controller):
                rule.action(app_controller)
        except KeyboardInterrupt:
            return
        except:
            logging.error('Rule', rule.name(), 'error, try to posepone...')


app.set_action_count(100)
app.foreach(on_perform)

if STATE_DEBUG_MODE:
    plt.show()

app.test(
    'com.intsig.camscanner',
    install_type="playstore",
    # debug=True,
)

# app.test(
#     'com.android.vending',
#     install=False,
#     debug=True,
# )

# app.test(
#     'com.android.deskclock',
#     install=False,
#     debug=True,
# )