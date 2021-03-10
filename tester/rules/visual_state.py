from ..app_controller import AppController
import networkx as nx
import matplotlib.pyplot as plt
import logging
import xml.etree.ElementTree as ET
import random
import zss
from zss import simple_distance, Node
from typing import Union
import time


class VisualState:
    def __init__(self, app_controller: AppController):
        activity, clickable_count, textinput_count = VisualState.get_state(
            app_controller)
        self.activity = activity
        self.clickable_count = clickable_count
        self.textinput_count = textinput_count

    def get_state(app_controller: AppController):
        logging.debug('get activity')
        activity = str(app_controller.get_current_activity())
        logging.debug('get clickables')
        clickable_count = len(app_controller.get_clickable_elements())
        logging.debug('get textinputs')
        textinput_count = len(
            app_controller.highlevel_query.find_all_text_input())
        return (
            activity,
            clickable_count,
            textinput_count
        )

    def __str__(self):
        return f"VisualState({self.activity}, {self.clickable_count}, {self.textinput_count})"

    def __eq__(self, other):
        if not other:
            return False
        return self.activity == other.activity and self.clickable_count == other.clickable_count and self.textinput_count == other.textinput_count


'''Edit Distance implementation'''


class ETVisualState:
    def __init__(self, app_controller: AppController):
        self.tree = ETVisualState.get_state(app_controller)
        self.name = random.randint(0, 100000)

    def get_state(app_controller: AppController):
        print('Getting source')
        source = app_controller.get_page_source()
        return ETVisualState.__convert_to_nx(source)

    def __convert_to_nx(xml):
        print('Creating graph')
        root = ET.fromstring(xml)
        tree = nx.Graph()
        queue = [(root, 'root', 0)]
        while len(queue) > 0:
            node, name, depth = queue[0]
            queue.pop(0)
            for index, child in enumerate(node):
                child_name = f"{depth + 1}_{index}"
                tree.add_edge(name, child_name)
                queue.append((child, child_name, depth + 1))
        return tree

    def __convert_to_zss(tree):
        T = nx.dfs_tree(tree, source='root')
        nodes_dict = {}
        for edge in T.edges():
            if edge[0] not in nodes_dict:
                nodes_dict[edge[0]] = zss.Node(edge[0])
            if edge[1] not in nodes_dict:
                nodes_dict[edge[1]] = zss.Node(edge[1])
            nodes_dict[edge[0]].addkid(nodes_dict[edge[1]])
        return nodes_dict

    def __str__(self):
        return f"ETVisualState({self.name})"

    def __eq__(self, other):
        if not other:
            return False
        print('Calculating sim')
        dist = simple_distance(ETVisualState.__convert_to_zss(self.tree)['root'], ETVisualState.__convert_to_zss(other.tree)['root'])
        print('Similarity ' + str(dist))
        return dist == 0


class VisualStateGraph:
    def __init__(self):
        self.fsm = nx.DiGraph()
        self.prev_state = None

    def add_transition(self, current_state: Union[VisualState, ETVisualState]):
        if current_state != self.prev_state:
            logging.debug('Detected state change to ' + str(current_state))
            self.fsm.add_edge(str(self.prev_state), str(current_state))
            self.prev_state = current_state

    def show(self):
        plt.clf()
        plt.cla()
        plt.title('Updated: ' + time.strftime("%H:%M:%S", time.localtime()))
        pos = nx.spiral_layout(self.fsm)
        nx.draw_networkx(self.fsm, with_labels=False, pos=pos)
        plt.pause(0.05)

    def nodes(self):
        return self.fsm.nodes()
