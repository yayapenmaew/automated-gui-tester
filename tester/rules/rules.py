from ..app_controller import AppController
from ..highlevel_query import Widget
import random


'''Rule Interface'''


class Rule:
    def name(self) -> str:
        return self.__class__.__name__

    def description(self) -> str:
        pass

    def match(self, app_controller: AppController) -> bool:
        pass

    def action(self, app_controller: AppController) -> None:
        pass


class ViewPagerRule(Rule):
    # def name(self):
    #     return "Found ViewPager"

    def description(self):
        return "Swipe left 5 times then back"

    def match(self, app_controller: AppController):
        return app_controller.highlevel_query.found_view_pager()

    def action(self, app_controller: AppController):
        for i in range(5):
            app_controller.swipe('left')
            app_controller.delay(1)
        app_controller.back()


class ImageButtonRule(Rule):

    # def name(self):
    #     return "Found ImageButton"

    def description(self):
        return "Click the button once"

    def match(self, app_controller: AppController):
        buttons = app_controller.highlevel_query.find_by_classname(
            Widget.IMAGE_BUTTON)
        return len(buttons)

    def action(self, app_controller: AppController):
        buttons = app_controller.highlevel_query.find_by_classname(
            Widget.IMAGE_BUTTON)
        for button in buttons:
            button.click()
            app_controller.delay(1)


class ActionBarRule(Rule):

    def __init__(self):
        self.tabVisited = set()
        self.finished = False

    # def name(self):
    #     return "Found ActionBar (Tabs)"

    def description(self):
        return "Loop through all tabs"

    def match(self, app_controller: AppController):
        if self.finished:
            return False
        tabs = app_controller.highlevel_query.find_by_classname(
            Widget.ACTION_BAR)
        return 0 < len(self.tabVisited) < len(tabs) if len(self.tabVisited) else len(tabs)

    def action(self, app_controller: AppController):
        tabs = app_controller.highlevel_query.find_by_classname(
            Widget.ACTION_BAR)
        for tab in tabs:
            tab_id = tab.get_attribute("resource-id")
            if tab_id in self.tabVisited:
                continue
            tab.click()
            self.tabVisited.add(tab_id)
            break
        if len(tabs) == len(self.tabVisited):
            self.finished = True


class SkipButtonRule(Rule):

    # def name(self):
    #     return "Found Skip button"

    def description(self):
        return "Press the skip button"

    def match(self, app_controller: AppController):
        buttons = app_controller.get_clickable_elements()
        for btn in buttons:
            if btn.get_attribute("text").lower() == "skip":
                btn.click()
                return True
        return False

    def action(self, app_controller: AppController):
        pass


class RandomTouchRule(Rule):
    # def name(self):
    #     return "Randomly touch the screen"
    def __init__(self, random_rate=0.3):
        self.random_rate = random_rate

    def description(self):
        return "Randomly touch the screen"

    def match(self, app_controller: AppController):
        return random.random() < self.random_rate

    def action(self, app_controller: AppController):
        app_controller.random_touch()


class RandomClickElementRule(Rule):
    # def name(self):
    #     return "Randomly touch the screen"
    def __init__(self, random_rate=0.3):
        self.random_rate = random_rate

    def description(self):
        return "Randomly click an element on the screen"

    def match(self, app_controller: AppController):
        return random.random() < self.random_rate

    def action(self, app_controller: AppController):
        app_controller.click_random_elements()


def initialize_rules():
    rules = [
        ViewPagerRule(),
        ImageButtonRule(),
        ActionBarRule(),
        SkipButtonRule(),
        RandomTouchRule(),
        RandomClickElementRule(),
    ]
    return rules
