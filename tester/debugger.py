import xml.etree.ElementTree as ET
from .app_controller import AppController


class Debugger():
    def walk_from_node(node, depth=0):
        tag = node.tag
        if 'text' in node.attrib and len(node.attrib["text"]):
            tag += ":" + node.attrib['text']
        if 'clickable' in node.attrib and node.attrib['clickable'].lower() == "true":
            tag = '\033[1;32;42m' + tag + '\033[m'
        print('  ' * depth + tag)
        for child in node:
            Debugger.walk_from_node(child, depth + 1)

    def __walk_xml(xml):
        root = ET.fromstring(xml)
        Debugger.walk_from_node(root)

    def debug(app_controller: AppController, inp):
        if inp in ["q", "quit"]:
            return False
        elif inp in ["s", "source"]:
            source = app_controller.get_page_source()
            print(source)
        elif inp in ["h", "help"]:
            print("Press q to exit")
        elif inp in ["hq"]:
            print("Highlevel query")
            method = input("Method to be called: ")
            try:
                print(getattr(app_controller.highlevel_query, method)())
            except Exception as err:
                print(err)
        elif inp in ["c"]:
            attrs = ['class', 'text', 'clickable']
            buttons = app_controller.get_clickable_elements()
            for button in buttons:
                print(','.join(map(lambda attr: button.get_attribute(attr), attrs)))
        elif inp in ["x", "xml"]:
            Debugger.__walk_xml(app_controller.get_page_source())
        else:
            print("Command", inp, "not found")
        return True
