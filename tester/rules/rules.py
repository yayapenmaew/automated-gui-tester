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
    def description(self):
        return "Swipe left 5 times"

    def match(self, app_controller: AppController):
        return app_controller.highlevel_query.found_view_pager()

    def action(self, app_controller: AppController):
        for i in range(5):
            app_controller.swipe('left')
            app_controller.delay(1)
        # app_controller.back()


class ImageButtonRule(Rule):
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
    def __init__(self, random_rate=0.3):
        self.random_rate = random_rate

    def description(self):
        return "Randomly touch the screen"

    def match(self, app_controller: AppController):
        return random.random() < self.random_rate

    def action(self, app_controller: AppController):
        app_controller.random_touch()


class RandomClickElementRule(Rule):
    def __init__(self, random_rate=0.3, self_inc=0.05):
        self.original_rate = random_rate
        self.random_rate = random_rate
        self.self_inc = self_inc

    def description(self):
        return "Randomly click an element on the screen"

    def match(self, app_controller: AppController):
        to_click = random.random() < self.random_rate
        if not to_click:
            self.random_rate += self.self_inc
        else:
            self.random_rate = self.original_rate
        return to_click

    def action(self, app_controller: AppController):
        app_controller.click_random_elements()


class RandomBackRule(Rule):
    def __init__(self, random_rate=0.2):
        self.random_rate = random_rate
    
    def description(self):
        return "Randomly press back button"

    def match(self, app_controller: AppController):
        return random.random() < self.random_rate

    def action(self, app_controller: AppController):
        return app_controller.back()


class BackToAppRule(Rule):
    def description(self):
        return "Back the the app under test"

    def match(self, app_controller: AppController):
        return not app_controller.is_on_current_package()
    
    def action(self, app_controller: AppController):
        app_controller.launch_app()


class FillTextFieldsRule(Rule):
    def __init__(self):
        Unique_username = "Sylphsgt098VWE"
        Unique_password = "u8zvTBYNnnGn"
        Email = "boomngongseniorproject@gmail.com"
        Unspecified_text = "YaaKcuMEgEsr"
        PhoneNo = "+66825999999"
        firstname = "iBvAdkFi"
        lastname = "eTJexjgnzPGS"
        Country = "Thailand"
        Province = "Bangkok"
        Day = "29"
        Month = "02"
        Year = "1990"
        FULLNAME = firstname + " " + lastname
        Card = "5105105105105100"
        Expir = "1225"
        CVV = "122"
        Postal = "10530"

        #search bar
        Search = "Mark"

        self.PII = {
            "email" : Email,
            "username" : Unique_username,
            "pass" : Unique_password,
            "pwd" : Unique_password,
            "pword" : Unique_password,
            "phone" : PhoneNo,
            "firstname" : firstname,
            "lastname" : lastname,
            "country" : Country, 
            "province" : Province, 
            "day" : Day,
            "month" : Month,
            "year" : Year,
            "search" : Search,
            "fullname" : FULLNAME,
            "gender" : "1",
            "card" : Card,
            "expir" : Expir,
            "cvc":CVV,
            "cvv":CVV,
            "post" : Postal
        }

    def description(self):
        return "Fill the textfields if the textfield has a matched id"

    def match(self, app_controller: AppController):
        self.text_inputs = app_controller.highlevel_query.find_all_text_input()
        return len(self.text_inputs) > 0
    
    def action(self, app_controller: AppController):
        for text_field_element in self.text_inputs:
            resource_id = text_field_element.get_attribute("resource-id")
            for pii in self.PII:
                if pii in resource_id.lower():
                    text_field_element.click()
                    text_field_element.send_keys(self.PII[pii])

class LoopThroughMenuRule(Rule):
    def __init__(self, random_rate=0.25):
        self.has_menu = False

    def description(self):
        return "Loop through menu items if exist"

    def match(self, app_controller: AppController):
        return False
        if not self.has_menu:
            self.has_menu = app_controller.highlevel_query.has_navigation_menu()
        return self.has_menu and random.random() < self.random_rate

    def action(self, app_controller: AppController):
        try:
            menu_buttons = app_controller.get_clickable_elements()
            index = random.randrange(0, len(menu_buttons))
            menu_buttons[index].click()
        except:
            pass


def initialize_rules(exclude=[]):
    rules = [
        ViewPagerRule(),
        ImageButtonRule(),
        ActionBarRule(),
        SkipButtonRule(),
        RandomTouchRule(),
        RandomClickElementRule(),
        BackToAppRule(),
        FillTextFieldsRule(),
        LoopThroughMenuRule(),
        RandomBackRule(),
    ]
    return list(filter(lambda rule: rule.__class__.__name__ not in exclude, rules))
