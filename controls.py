import copy
import menu


def underscore_to_camelcase(word):
    head, *tail = word.split('_')
    return head + ''.join(word.capitalize() for word in tail)


class Align:
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"
    CENTER = "center"


class Orientation:
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    BOTH = "both"
    NONE = "none"


class BorderType:
    SUNKEN = "sunken"
    LINE = "line"
    NONE = "none"


class ButtonType:
    PUSHBUTTON = "pushbutton"
    PUSHBOX = "pushbox"
    CHECKBOX = "checkbox"
    RADIO = "radio"


class BarDirection:
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    CLOCKWISE = "clockwise"
    COUNTERCLOCKWISE = "counterclockwise"


class ImageMode:
    CENTER = "center"
    STRETCH = "stretch"
    TILE = "tile"


class Lock:
    NONE = "none"
    LEFT = "left"
    RIGHT = "right"


class Macro:
    command = ""
    is_disabled = False
    map_to = ""
    name = None  # no default


def first_lower(string):
    return string[0].lower() + string[1:]


class Control:
    anchor1 = None
    anchor2 = None
    background_color = "#FFF"
    border = None
    drop_zone = False
    flash = 0
    focus = False
    font_family = ""
    font_size = 0
    font_style = ""
    id = None  # is readonly, no default
    is_disabled = False
    is_transparent = False
    is_visible = True
    on_size = ""
    pos = 0, 0
    right_click = False
    size = 0, 0
    text_color = "#000"
    type = None  # is readonly, no default

    parent = None

    # not Control's
    text = None
    button_type = None
    can_check = None
    is_checked = None
    qt_code = None
    qt_code_bottom = None
    qt_class = ''

    idx = 0

    def __init__(self, element):
        self.__class__.idx += 1
        self.idx = self.__class__.idx

        self.id = element['id']
        self.parent = element.get('parent')

        for k, v in element.items():
            setattr(self, k, v)

        self.qt_name = ''
        if not self.qt_class:
            self.qt_class = self.__class__.__name__

        if self.id:
            self.qt_name = self.id
        elif self.qt_class:
            self.qt_name = 'self.{}'.format(first_lower(self.qt_class))
            if self.idx > 1:
                self.qt_name += '_{}'.format(self.idx)

    def __repr__(self):
        d = copy.deepcopy(self.__dict__)
        del d['parent']
        return '{} {}'.format(self.__class__.__name__, d)

    def add_code_line(self, text, *args, method=True, bottom=False):
        prefix = '        '
        if method:
            prefix += 'self.{}.'.format(self.qt_name)

        text = prefix + text.format(*args)
        if bottom:
            self.qt_code_bottom.append(text)
        else:
            self.qt_code.append(text)

    def generate_code_bottom(self):
        return '\n'.join(self.qt_code_bottom)

    def generate_code(self):
        if self.parent:
            # print(self.parent)
            # self.centralWidget
            self.add_code_line('self.{} = {}(self.{}, id="{}")', self.qt_name, self.qt_class, self.parent.qt_name, self.qt_name.lower(), method=False)
        else:
            self.add_code_line('self.{} = {}(id="{}")', self.qt_name, self.qt_class, self.qt_name.lower(), method=False)

        if self.button_type == ButtonType.PUSHBOX or self.can_check:
            self.add_code_line('setCheckable(True)')

        if self.is_checked:
            self.add_code_line('setChecked(True)')

        if self.text:
            self.add_code_line('setText("{}")', self.text)

        if self.anchor1:
            self.add_code_line('setAnchor1({}, {})', *self.anchor1)

        if self.anchor2:
            self.add_code_line('setAnchor2({}, {})', *self.anchor2)

        if not self.pos:  # fixme
            self.pos = (0, 0)
        if self.pos and self.size:
            self.add_code_line('setBaseGeometry({}, {}, {}, {})', *self.pos, *self.size)

        if self.id:
            self.add_code_line('setObjectName("{}")', self.id)

        if self.anchor1 or self.anchor2:
            self.add_code_line('self.mainWindow.resized.connect(self.{}.windowResizeEvent)', self.qt_name, method=False)


class Main(Control):
    alpha = 255
    can_close = True
    can_minimize = True
    can_resize = True
    can_scroll = None
    icon = ""
    image = ""
    image_mode = ImageMode.STRETCH
    is_default = False
    is_minimized = False
    is_maximized = False
    is_pane = False
    keep_aspect = False
    macro = ""
    menu = None
    on_close = ""
    statusbar = True  # False in documentation, but it cannot be true
    title = ""
    titlebar = True
    transparent_color = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = []
        self.qt_code = []
        self.qt_code_bottom = []


class Window(Main):
    is_pane = False

    def add_code_line(self, text, *args, method=True):
        prefix = '        '
        if method:
            prefix += 'self.{}.'.format(self.qt_name)

        text = prefix + text.format(*args)
        self.qt_code.append(text)

    def generate_code(self):
        self.qt_name = 'mainWindow'
        qt = self.add_code_line

        self.add_code_line('self.{} = MainWindow', self.qt_name, method=False)
        if self.title:
            self.add_code_line('setWindowTitle("{}")', self.title)
        if self.size != (0, 0):
            width, height = self.size
            if self.statusbar:
                height += 39
            self.add_code_line('setBaseSize({}, {})', width, height)

        # widget = Pane()
        # widget.qt_name = 'centralWidget'
        # widget.parent = self
        # widget.generate_code()

        widget_name = 'centralWidget'
        qt('self.{} = Pane(self.{}, id="{}")', widget_name, self.qt_name, self.qt_name.lower(), method=False)
        qt('setCentralWidget(self.{})', widget_name)

        if self.statusbar:
            qt('', method=False)
            qt('self.statusBar = QtWidgets.QStatusBar(self.{})', self.qt_name, method=False)
            qt('self.statusBar.showMessage("water")', method=False)
            qt('self.statusBar.setFixedHeight(15)', method=False)
            qt('setStatusBar(self.statusBar)')

        if self.menu:
            qt('', method=False)
            qt('self.menuBar = QtWidgets.QMenuBar(self.{})', self.qt_name, method=False)
            qt('self.menuBar.setGeometry(QtCore.QRect(0, 0, 640, 21))', method=False)
            qt('self.menuBar.setObjectName("menuBar")', method=False)
            qt('setMenuBar(self.menuBar)')

            qt('', method=False)
            for group in self.menu.groups:
                qt('self.{}Group = QtWidgets.QActionGroup(self.{})', group, self.qt_name, method=False)

            for category in self.menu.categories:
                category_id = 'menu' + category.id
                qt('', method=False)
                qt('self.{} = QtWidgets.QMenu(self.menuBar)', category_id, method=False)
                qt('self.{0}.setObjectName("{0}")', category_id, method=False)
                qt('self.{}.setTitle("{}")', category_id, category.name, method=False)
                qt('self.menuBar.addAction(self.{}.menuAction())', category_id, method=False)

                for action in category.actions:
                    print(action)
                    if action is None:  # separator
                        qt('', method=False)
                        qt('self.{}.addSeparator()'.format(category_id), method=False)
                    elif isinstance(action, menu.Action):
                        action_id = 'action' + action.id.capitalize()
                        qt('', method=False)
                        if action.group:
                            qt(
                                'self.{} = QtWidgets.QAction(self.{}Group)'.format(action_id, action.group),
                                method=False
                            )
                        else:
                            qt('self.{} = QtWidgets.QAction(self.{})'.format(action_id, category_id), method=False)
                        qt('self.{0}.setObjectName("{0}")'.format(action_id), method=False)
                        qt('self.{}.setText("{}")'.format(action_id, action.name), method=False)
                        if action.can_check:
                            qt('self.{}.setCheckable(True)'.format(action_id), method=False)
                        if action.is_checked:
                            qt('self.{}.setChecked(True)'.format(action_id), method=False)
                        qt('self.{}.addAction(self.{})'.format(category_id, action_id), method=False)

        self.qt_name = widget_name
        for child in self.children:
            qt('', method=False)
            child.qt_code = self.qt_code
            child.qt_code_bottom = self.qt_code_bottom
            child.generate_code()

        return '\n'.join(self.qt_code)


class Pane(Main):
    is_pane = True
    qt_class = "Pane"

    def generate_code(self):
        super().generate_code()
        for child in self.children:
            self.add_code_line('', method=False)
            child.qt_code = self.qt_code
            child.qt_code_bottom = self.qt_code_bottom
            child.generate_code()

        self.add_code_line('setAutoFillBackground(True)', method=True)
        self.add_code_line(f'palette = self.{self.qt_name}.palette()', method=False)
        self.add_code_line(f'palette.setColor(self.{self.qt_name}.backgroundRole(), QtCore.Qt.green)', method=False)
        self.add_code_line('setPalette(palette)', method=True)

        return '\n'.join(self.qt_code)


class Label(Control):
    align = Align.CENTER
    image = ""
    image_mode = ImageMode.STRETCH
    keep_aspect = False
    stretch = False  # deprecated
    text = ""
    text_wrap = False


class Button(Control):
    button_type = ButtonType.PUSHBUTTON
    command = ""
    group = ""
    image = ""
    is_checked = False
    is_flat = False
    text = ""

    idx = 0
    qt_class = "PushButton"


class Input(Control):
    allow_html = False
    command = ""
    is_password = False
    multi_line = False
    no_command = False
    text = ""

    idx = 0
    qt_class = "Input"


class Output(Control):
    enable_http_images = False
    image = ""
    link_color = "#00F"
    max_lines = 1000
    style = ""
    visited_color = "#F0F"


class OnShowMixin:
    on_show = ""
    on_hide = ""

    def __init__(self, element):
        super().__init__(element)
        self.on_show = element.get('on_show', {}).get('.winset')
        self.on_hide = element.get('on_hide', {}).get('.winset')

    def generate_code(self):
        super().generate_code()

        def get_value(key, value):
            attr_name = key.split('.')[-1]
            if attr_name in ('left', 'right'):
                value = f'"{value}"'
            return value

        def generate_action_code(action, indent=4):
            for key, value in action.items():
                self.add_code_line(f'{" "*indent}set_widget_attr("{key}", {get_value(key, value)})', method=False)

        def generate_toggle_code(attr_name):
            attr = getattr(self, attr_name)
            if attr:
                self.add_code_line('', method=False)
                self.add_code_line(f'def {attr_name}():', method=False)
                for action in attr:
                    if all(key in action for key in ('if', 'then', 'else')):

                        conditions = []
                        for condition in action['if']:
                            for key, value in condition.items():  # FIXME
                                conditions.append(f'get_widget_attr("{key}") == {get_value(key, value)}')

                        conditions = ' and '.join(conditions)
                        self.add_code_line(f'    if {conditions}:', method=False)

                        for subaction in action['then']:
                            generate_action_code(subaction, indent=8)

                        if action['else']:
                            self.add_code_line('    else:', method=False)

                        for subaction in action['else']:
                            generate_action_code(subaction, indent=8)
                    else:
                        generate_action_code(action)

                self.add_code_line('', method=False)
                self.add_code_line(f'{underscore_to_camelcase(attr_name)} = {attr_name}', method=True)

        generate_toggle_code('on_show')
        generate_toggle_code('on_hide')

class Browser(OnShowMixin, Control):
    auto_format = True
    show_history = False
    show_url = False
    use_title = False

    def __init__(self, element):
        super().__init__(element)
        print("hello")

    def generate_code(self):
        super().generate_code()

        self.add_code_line('setAutoFillBackground(True)', method=True)
        self.add_code_line(f'palette = self.{self.qt_name}.palette()', method=False)
        self.add_code_line(f'palette.setColor(self.{self.qt_name}.backgroundRole(), QtCore.Qt.yellow)', method=False)
        self.add_code_line('setPalette(palette)', method=True)


class Map(OnShowMixin, Control):
    drop_zone = True
    icon_size = 0
    letterbox = True
    style = ""
    text_mode = False
    view_size = 0
    zoom = 0

    def __init__(self, element):
        super().__init__(element)
        print("hello")

    def generate_code(self):
        super().generate_code()

        self.add_code_line('setAutoFillBackground(True)', method=True)
        self.add_code_line(f'palette = self.{self.qt_name}.palette()', method=False)
        self.add_code_line(f'palette.setColor(self.{self.qt_name}.backgroundRole(), QtCore.Qt.black)', method=False)
        self.add_code_line('setPalette(palette)', method=True)


class Info(OnShowMixin, Control):
    drop_zone = True
    highlight_color = "#0F0"
    multi_line = True
    on_tab = ""
    prefix_color = None
    suffix_color = None
    tab_background_color = None
    tab_font_family = None
    tab_font_size = 0
    tab_text_color = None

    def __init__(self, element):
        super().__init__(element)
        print("hello")

    def generate_code(self):
        super().generate_code()

        self.add_code_line('setAutoFillBackground(True)', method=True)
        self.add_code_line(f'palette = self.{self.qt_name}.palette()', method=False)
        self.add_code_line(f'palette.setColor(self.{self.qt_name}.backgroundRole(), QtCore.Qt.darkBlue)', method=False)
        self.add_code_line('setPalette(palette)', method=True)

class Child(Control):
    is_vert = False
    left = None
    lock = Lock.NONE
    right = None
    show_splitter = True
    splitter = 50
    qt_class = 'Child'
    # self.pushButton = QtWidgets.QPushButton(self.mainvsplit)
    # self.pushButton.setObjectName("pushButton")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def generate_code(self):
        super().generate_code()
        orientation = "Horizontal"
        if self.is_vert:
            orientation = "Vertical"

        self.add_code_line(f'setOrientation(QtCore.Qt.{orientation})', method=True)
        self.add_code_line('setOpaqueResize(True)', method=True)
        self.add_code_line('setChildrenCollapsible(True)', method=True)

        self.add_code_line('setAutoFillBackground(True)', method=True)
        self.add_code_line(f'palette = self.{self.qt_name}.palette()', method=False)
        self.add_code_line(f'palette.setColor(self.{self.qt_name}.backgroundRole(), QtCore.Qt.red)', method=False)
        self.add_code_line('setPalette(palette)', method=True)

        if self.left:
            self.add_code_line(f'left = get_widget("{self.left}")', method=True, bottom=True)

        if self.right:
            self.add_code_line(f'right = get_widget("{self.right}")', method=True, bottom=True)

        # self.mainvsplit.setAutoFillBackground(True)
        # palette = self.mainvsplit.palette()
        # palette.setColor(self.mainvsplit.backgroundRole(), QtCore.Qt.red)  # QColor(255, 0, 0, 255)
        # self.mainvsplit.setPalette(palette)


class Tab(Control):
    current_tab = ""
    multi_line = True
    on_tab = ""
    tab_font_style = ""
    tabs = ""


class Grid(Control):
    cell_span = 1, 1
    cells = 0, 0
    current_cell = 0, 0
    drop_zone = True
    enable_http_images = False
    highlight_color = "#0F0"
    is_list = False
    line_color = "#C0C0C0"
    link_color = "#00F"
    show_lines = Orientation.BOTH
    show_names = True
    small_icons = False
    style = ""
    visited_color = "#F0F"


class Bar(Control):
    angle1 = 0
    angle2 = 180
    bar_color = None
    dir = BarDirection.EAST
    is_slider = False
    on_change = ""
    value = 0
    width = 10
