import re
import operator


class Widget:
    TEXT_VIEW = "android.widget.TextView"
    EDIT_TEXT = "android.widget.EditText"
    VIEW_PAGER = "androidx.viewpager.widget.ViewPager"


class PageType:
    LOGIN = "LOGIN"
    REGISTER = "REGISTER"


class HighlevelQuery:
    def __init__(self, driver):
        self.driver = driver

    def __is_element_has_attr(self, element, attribute={}):
        for attr, value in attribute.items():
            real_value = element.get_attribute(attr)

            if type(value) == re.Pattern:
                if not value.search(real_value):
                    return False
            else:
                if type(value) == bool:
                    value = str(value).lower()
                elif type(value) in [int, float]:
                    value = str(value)

                if not real_value or value != real_value:
                    return False

        return True

    def __find_by_classname(self, class_name, attr={}):
        elements = self.driver.find_elements_by_class_name(class_name)
        if attr:
            return list(filter(lambda element: self.__is_element_has_attr(element, attr), elements))
        else:
            return elements

    def password_field_count(self):
        return len(self.__find_by_classname(Widget.EDIT_TEXT, {"password": True}))

    def has_login_with_button(self):
        return len(self.__find_by_classname(Widget.TEXT_VIEW, {
            "text": re.compile("(เข้าสู่ระบบ|Login|Continue).*(Facebook|Google|Twitter|Apple|Email)", re.IGNORECASE)
        })) > 0

    def find_all_text_input(self):
        return self.__find_by_classname(Widget.EDIT_TEXT, { "focusable": True })

    def fill_text_input(self, values):
        # values = { "email": "test@test.com", "password": "password", "pwd": "password", "pword": "password" }
        text_inputs = self.find_all_text_input()
        for text_input in text_inputs:
            resource_id = text_input.get_attribute("resource-id").lower()
            for id in values:
                if id in resource_id:
                    text_input.click()
                    text_input.send_keys(values[id])

    def page_type(self):
        score = {
            PageType.LOGIN: 0,
            PageType.REGISTER: 0
        }

        # Count text fields that have password attribute.
        password_field_count = self.password_field_count()
        if password_field_count > 1:
            return PageType.REGISTER
        elif password_field_count > 0 or self.has_login_with_button():
            return PageType.LOGIN

        # Return PageType with maximum score
        return max(score.items(), key=operator.itemgetter(1))[0]

    def is_login_page(self):
        return self.__has_password_field

    def found_view_pager(self):
        return self.__find_by_classname(Widget.VIEW_PAGER)