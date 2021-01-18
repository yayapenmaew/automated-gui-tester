import re
import operator


class Widget:
    TEXT_VIEW = "android.widget.TextView"
    EDIT_TEXT = "android.widget.EditText"


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
                print(real_value)
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

    def __has_password_field(self):
        return len(self.__find_by_classname(Widget.EDIT_TEXT, {"password": True})) > 0

    def __has_login_with_button(self):
        return len(self.__find_by_classname(Widget.TEXT_VIEW, {
            "text": re.compile("(เข้าสู่ระบบ|Login|Continue).*(Facebook|Google|Twitter|Apple|Email)", re.IGNORECASE)
        })) > 0

    def page_type(self):
        score = {
            PageType.LOGIN: 0,
            PageType.REGISTER: 0
        }

        if self.__has_password_field():
            score[PageType.LOGIN] += 1
        if self.__has_login_with_button():
            score[PageType.LOGIN] += 1

        # Return PageType with maximum score
        return max(stats.items(), key=operator.itemgetter(1))[0]

    def is_login_page(self):
        return self.__has_password_field
