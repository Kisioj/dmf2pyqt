import controls
from template import TEMPLATE
import menu
import json


def to_ints(string, delimiter):
    return list(map(int, string.split(delimiter)))

DEFAULT_VALUES_MAP = {
    'none': None,
    'false': False,
    'true': True,
}

ATTRIBUTE_MAP = {
    'anchor1': ',',
    'anchor2': ',',
    'pos': ',',
    'size': 'x',
    'cell_span': 'x',
    'cells': 'x',
    'current_cell': 'x',
}

TYPES_MAP = {
    'WINDOW': controls.Window,
    'PANE': controls.Pane,
    'INPUT': controls.Input,
    'BUTTON': controls.Button,
    'MAP': controls.Map,
    'OUTPUT': controls.Output,
    'CHILD': controls.Child,
    'BROWSER': controls.Browser,
    'INFO': controls.Info,
}


class DMFParser:
    def __init__(self):
        self.macros = []
        self.menus = []
        self.windows = []
        self.category = None
        self.element = None

    @staticmethod
    def _parse_key_value(string):
        if '"' in string:
            key, value = string.split()
            value = value.strip('"')
        else:
            key, value = string, None
        return key, value

    @staticmethod
    def _parse_key_eq_sign_value(string):
        key, value = string.split(' = ')
        return key, value.strip('"')

    def _parse_category(self, line):
        category_type, category_id = self._parse_key_value(line)
        self.category = {
            'type': category_type,
            'id': category_id,
            'elements': []
        }
        if category_type == 'macro':
            self.macros.append(self.category)
        elif category_type == 'menu':
            self.menus.append(self.category)
        elif category_type == 'window':
            self.windows.append(self.category)

    def _parse_element(self, line):
        line = line.lstrip('\t')
        element_type, element_id = self._parse_key_value(line)
        self.element = {
            'type': element_type,
            'id': element_id,
            'attributes': {},
            # 'parent': self.category,
        }
        self.category['elements'].append(self.element)

    def _parse_attribute(self, line):
        line = line.lstrip('\t')
        name, value = self._parse_key_eq_sign_value(line)
        name = name.replace('-', '_')
        value = value.replace('-', '_')
        value = value.strip('\n"')
        if value in DEFAULT_VALUES_MAP:
            value = DEFAULT_VALUES_MAP[value]
        elif name in ATTRIBUTE_MAP:
            delimiter = ATTRIBUTE_MAP[name]
            value = to_ints(value, delimiter)
        elif value.isdigit():
            value = int(value)
        elif name == 'saved_params':
            value = value.split(';')

        if name == 'type':
            if value == 'MAIN':
                value = 'WINDOW'
            self.element['type'] = value
        else:
            self.element['attributes'][name] = value

    def parse_file(self, filename):
        with open(filename) as f:
            for line in f:
                if not line:
                    continue
                if line.startswith('\t\t'):
                    self._parse_attribute(line)
                elif line.startswith('\t'):
                    self._parse_element(line)
                else:
                    self._parse_category(line)

        for window in self.windows:
            element = window['elements'][0]
            # element.pop('parent')
            if 'is_pane' in element['attributes']:
                is_pane = element['attributes'].pop('is_pane')
                if is_pane:
                    element['type'] = 'PANE'


def main():
    parser = DMFParser()
    parser.parse_file('byond.dmf')

    with open('byond.json', 'w') as f:
        f.write(json.dumps(parser.windows, indent=4))
    print(json.dumps(parser.windows, indent=4))

    ui_menus = []
    for menu_bar in parser.menus:
        ui_menus.append(menu.Bar(menu_bar))

    ui_windows = []
    for window in parser.windows:
        # print()
        control = window['elements'][0]
        container = TYPES_MAP[control['type']](control)
        if container.menu:
            for ui_menu in ui_menus:
                if container.menu == ui_menu.id:
                    container.menu = ui_menu

        ui_windows.append(container)
        # print(container)
        for control in window['elements'][1:]:
            element = TYPES_MAP[control['type']](control)
            container.children.append(element)
            element.parent = container
            # print('\t{}'.format(element))

    for ui_window in ui_windows:
        print()
        print(ui_window)
        for element in ui_window.children:
            print('\t{}'.format(element))

    print(ui_windows[0].generate_code())

    result = TEMPLATE.format(ui_windows[0].generate_code())
    with open('pyqt5.py', 'w') as f:
        f.write(result)
    print(result)

if __name__ == '__main__':
    main()
