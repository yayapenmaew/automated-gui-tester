#!/usr/bin/env python3
from tester.application import DynamicTestingApplication
from tester.app_controller import AppController
from tester.rules.rules import initialize_rules
from tester.rules.visual_state import VisualState, VisualStateGraph
from analyzer.PI_detection import VULPIXAnalyzer
import time
import logging
import os
import sys
import random


class TesterConfig:
    DEVICE_NAME = "K6T6R17909001485"
    PROXY_HOST = "192.168.1.249"
    ANDROID_VERSION = "7.0"
    N_ACTIONS = 50


def run_benchmark(app_id, mode, rules=[], install=False, timeout=None):
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
    states = VisualStateGraph()

    time_history = [time.time()]
    state_tracking = []

    if mode == "ga" or mode == "rule_based":
        def on_perform(app_controller: AppController, step):
            if timeout:
                if time_history[-1] - time_history[0] > timeout:
                    return
                time_history.append(time.time())

            if app_controller.is_on_current_package():
                current_state = VisualState(app_controller)
                old_len = len(states.nodes())
                states.add_transition(current_state)
                if len(states.nodes()) > old_len:
                    state_tracking.append(time.time() - time_history[0])

            for rule in rules:
                try:
                    if rule.match(app_controller):
                        # print(rule.name())
                        rule.action(app_controller)
                except KeyboardInterrupt:
                    return
                except:
                    pass
    elif mode == "mankey":
        action_count = 300
        app.set_action_count(action_count)

        # start_time = time.time()

        start_times = []

        activity_counts = [0]
        package_counts = [0]

        def on_perform(app_controller: AppController, step):
            if step == 0:
                start_times.append(time.time())

            start_time = start_times[0]
            if timeout:
                if time_history[-1] - time_history[0] > timeout:
                    return
                time_history.append(time.time())

            if app_controller.is_on_current_package():
                current_state = VisualState(app_controller)
                old_len = len(states.nodes())
                states.add_transition(current_state)
                if len(states.nodes()) > old_len:
                    state_tracking.append(time.time() - time_history[0])

            driver = app_controller.driver

            on_current_package = app_controller.is_on_current_package()

            activity_count = activity_counts[-1]
            package_count = package_counts[-1]

            if(not on_current_package and package_count >= 5):
                activity_count = 0
                try:
                    driver.launch_app()
                except:
                    pass
            else:
                # allow pop-up, browser and default application for 10 actions

                if(not on_current_package):
                    package_count += 1

                if (activity_count >= 50):
                    activity_count = 0
                    if time.time() - start_time >= 200:
                        return False

                    try:
                        driver.launch_app()
                    except:
                        pass
                else:
                    if time.time() - start_time >= 200:
                        return False
                    try:
                        prev_activity = driver.current_activity
                        Clickable_Elements = driver.find_elements_by_android_uiautomator(
                            "new UiSelector().clickable(true)")
                        Textinput_Elements = []
                        for element in Clickable_Elements:
                            if element.get_attribute("class") == "android.widget.EditText" and element.get_attribute("focusable") == "true":
                                Textinput_Elements.append(element)
                            if time.time() - start_time >= 200:
                                return False

                        Clickable_Elements = list(
                            set(Clickable_Elements) - set(Textinput_Elements))
                        # iMonkey
                        # random action  1 - 100
                        if time.time() - start_time >= 200:
                            return False
                        if (len(Clickable_Elements) == 0):
                            random_action = random.randrange(81, 101)
                        elif (len(Textinput_Elements) == 0):
                            random_action = random.randrange(21, 101)
                        else:
                            random_action = random.randrange(1, 101)

                        # 0, filled a random text field | or fill all ? 20 %
                        if(random_action < 21):
                            temp = random.randrange(len(Textinput_Elements))
                            app_controller.highlevel_query.fill_text_input()

                        # 1 randomly click on clickable element 60%
                        elif (random_action >= 21 and random_action < 81):
                            temp = random.randrange(len(Clickable_Elements))
                            Clickable_Elements[temp].click()
                        # Monkey
                        # 15 % swipe randomly (4 direction)
                        elif (random_action >= 81 and random_action < 96):
                            width, height = app_controller.get_window_size()
                            # height = window_size["height"]
                            # width = window_size["width"]
                            temp = random.randrange(4)
                            # driver.swipe(startX, startY, endX, endY, duration)
                            if temp == 0:
                                try:
                                    driver.swipe(width/2, height/2,
                                                 width/2, height/4, 400)
                                except:
                                    driver.swipe(height/2, width/2,
                                                 height/2, width/4, 400)
                            if temp == 1:
                                try:
                                    driver.swipe(width/2, height/2,
                                                 width/2, height*3/4, 400)
                                except:
                                    driver.swipe(height/2, width/2,
                                                 height/2, width*3/4, 400)

                            if temp == 2:
                                try:
                                    driver.swipe(width/2, height/2,
                                                 width/4, height/4, 400)
                                except:
                                    driver.swipe(height/2, width/2,
                                                 height/4, width/4, 400)

                            if temp == 3:
                                try:
                                    driver.swipe(width/2, height/2,
                                                 width*3/4, height/4, 400)
                                except:
                                    driver.swipe(height/2, width/2,
                                                 height*3/4, width/4, 400)

                        # 5% monkey
                        elif (random_action >= 96):
                            temp = random.randrange(2)
                            if temp == 0:
                                app_controller.random_touch()
                            if temp == 1:
                                driver.press_keycode(4)

                    except:
                        try:
                            driver.launch_app()
                        except:
                            pass

                    curr_activity = driver.current_activity

                    if(curr_activity == prev_activity):
                        activity_count += 1

            activity_counts.append(activity_count)
            package_counts.append(package_count)

            if time.time() - start_time >= 200:
                return False

    app.foreach(on_perform)

    app.test(
        app_id,
        install_type='playstore',
        install=install,
        # proxy=False,
        reset_state=False
    )

    with open('tracking.txt', 'a') as fp:
        fp.write(app_id + "\t" + mode + "\t" +
                 ','.join([str(e) for e in state_tracking]) + "\n")

    return len(states.nodes())


def append_score(app_name, mode, score, vulpix_score, running_time, filename="model_comparison.txt"):
    with open(filename, "a") as fp:
        fp.write(app_name + "\t" + mode + "\t" + str(score) + "\t" +
                 str(vulpix_score) + "\t" + str(running_time) + "\n")


if __name__ == '__main__':
    app_list = sys.argv[1]
    with open(app_list, 'r') as fp:
        for line in fp:
            app_id = line.strip()
            installed = False
            if '%' in app_id:
                continue
            try:
                for mode in ["ga", "rule_based", "mankey"]:
                    if mode == "ga":
                        rules = initialize_rules(include=[
                            "ViewPagerRule",
                            "ImageButtonRule",
                            "ActionBarRule",
                            "RandomClickElementRule",
                            "FillTextFieldsRule",
                            "BackToAppRule",
                        ])
                    else:
                        rules = initialize_rules()
                    t_start = time.time()
                    score = run_benchmark(app_id, mode, rules, not installed)
                    t_end = time.time()

                    try:
                        vulpix_score, vulpix_pi = VULPIXAnalyzer.analyze(app_id)
                    except:
                        vulpix_score = -1

                    append_score(app_id, mode, score, vulpix_pi, t_end - t_start)
                    installed = True
                    time.sleep(10)
            except KeyboardInterrupt:
                print('Terminating ...')
                break
            except Exception as e:
                print('Skip error', e)
