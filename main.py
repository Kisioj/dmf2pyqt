import controls
from template import TEMPLATE
import menu
import json
from dmf2json.dmf2json import DMFParser as DMF2JSONParser
import collections


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


def main(filename_dmf='byond.dmf', filename_json='byond.json', filename_pyqt='byond.py'):
    parser = DMF2JSONParser(input_filename=filename_dmf, output_filename=filename_json)
    parser.parse()
    # print(parser.to_json())

    ui_menubars = collections.OrderedDict()
    for menubar_data in parser.menubars:
        ui_menubars[menubar_data['id']] = menu.MenuBar(menubar_data)

    ui_windows = []
    for window_data in parser.windows:
        window = TYPES_MAP[window_data['type']](window_data)
        for control in window.controls:
            element = TYPES_MAP[control['type']](control)
            element.parent = window
            window.children.append(element)
        window.menu = ui_menubars.get(window.menu)
        ui_windows.append(window)

    # print("-")
    # print(ui_windows[0].generate_code())
    # print("-")
    result = TEMPLATE.format('\n        \n'.join(window.generate_code() for window in ui_windows))
    # print(ui_windows[2])
    with open('pyqt5.py', 'w') as f:
        f.write(result)
    # print(result)

if __name__ == '__main__':
    main()
