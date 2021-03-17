import re
import operator
import xml.etree.ElementTree as ET


class Widget:
    TEXT_VIEW = "android.widget.TextView"
    IMAGE_VIEW = "android.widget.ImageView"
    EDIT_TEXT = "android.widget.EditText"
    VIEW_PAGER = "androidx.viewpager.widget.ViewPager"
    IMAGE_BUTTON = "android.widget.ImageButton"
    ACTION_BAR = "android.app.ActionBar$Tab"
    LINEAR_LAYOUT = "android.widget.LinearLayout"
    BUTTON = "android.widget.Button"
    VIEW = "android.view.View"


class PageType:
    LOGIN = "LOGIN"
    REGISTER = "REGISTER"


# def walk_from_node(node, depth=0):
#     tag = node.tag
#     if 'text' in node.attrib and len(node.attrib["text"]):
#         tag += ":" + node.attrib['text']
#     if 'clickable' in node.attrib and node.attrib['clickable'].lower() == "true":
#         tag = '\033[1;32;42m' + tag + '\033[m'
#     print('  ' * depth + tag)
#     for child in node:
#         walk_from_node(child, depth + 1)


class HighlevelQuery:
    def __init__(self, driver):
        self.driver = driver

    def __is_element_has_attr(self, element, attribute={}):
        for attr, value in attribute.items():
            try:
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
            except:
                return False

        return True

    def __find_by_classname(self, class_name, attr={}):
        elements = self.driver.find_elements_by_class_name(class_name)
        if attr:
            return list(filter(lambda element: self.__is_element_has_attr(element, attr), elements))
        else:
            return elements

    def find_by_classname(self, class_name, attr={}):
        return self.__find_by_classname(class_name, attr)

    def password_field_count(self):
        return len(self.__find_by_classname(Widget.EDIT_TEXT, {"password": True}))

    def has_login_with_button(self):
        return len(self.__find_by_classname(Widget.TEXT_VIEW, {
            "text": re.compile("(เข้าสู่ระบบ|Login|Continue).*(Facebook|Google|Twitter|Apple|Email)", re.IGNORECASE)
        })) > 0

    def find_all_text_input(self):
        return self.__find_by_classname(Widget.EDIT_TEXT, {"focusable": True})

    def fill_text_input(self, values):
        # values = { "email": "test@test.com", "password": "password", "pwd": "password", "pword": "password" }
        text_inputs = self.find_all_text_input()
        for text_input in text_inputs:
            resource_id = text_input.get_attribute("resource-id").lower()
            for id in values:
                if id in resource_id:
                    text_input.click()
                    text_input.send_keys(values[id])

    def has_navigation_menu(self):
        MIN_MENU_COUNT = 3

        def count_matched_classname(node, classname):
            if node.tag == classname:
                return 1
            count = 0
            for child in node:
                count += count_matched_classname(child, classname)
            return count

        def find_nav_from_source(node):
            menu_count = 0
            
            for child in node:
                if 'clickable' in child.attrib and child.attrib["clickable"].lower() == "true":
                    if count_matched_classname(child, Widget.TEXT_VIEW) == 1 and count_matched_classname(child, Widget.IMAGE_VIEW) == 1:
                        menu_count += 1
                    
            if menu_count >= MIN_MENU_COUNT:
                # walk_from_node(node)
                return True

            for child in node:
                if find_nav_from_source(child):
                    return True
            return False

        xml = self.driver.page_source
        root = ET.fromstring(xml)
        return find_nav_from_source(root)

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
