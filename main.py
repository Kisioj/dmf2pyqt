import controls
from template import TEMPLATE
import menu
import json
from dmf2json.dmf2json import DMFParser


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


def main():
    parser = DMFParser()
    parser.parse_file('byond.dmf')

    with open('byond.json', 'w') as f:
        f.write(json.dumps(parser.windows, indent=4))
    print(json.dumps(parser.windows, indent=4))

    ui_menus = []
    for menu_bar in parser.menubars:
        ui_menus.append(menu.Bar(menu_bar))

    ui_windows = []
    for window in parser.windows:
        # print()
        control = window['controls'][0]
        container = TYPES_MAP[control['type']](control)
        if container.menu:
            for ui_menu in ui_menus:
                if container.menu == ui_menu.id:
                    container.menu = ui_menu

        ui_windows.append(container)
        # print(container)
        for control in window['controls'][1:]:
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
