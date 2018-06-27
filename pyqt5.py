#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication, QStyleFactory
from PyQt5 import QtCore, QtGui, QtWidgets

NULL_SIZE = QtCore.QSize(-1, -1)

SHOW_BROWSER = True
SHOW_INFO = True
SHOW_MAP = True

widget_id_2_widget = {}


def get_widget(fullpath):
    widget_id, *path = fullpath.split('.')
    widget = widget_id_2_widget[widget_id]
    for widget_id in path:
        widget = widget.child_id_2_widget[widget_id]
    return widget


def get_widget_attr(widget_attr_path):
    *fullpath, attr_name = widget_attr_path.split('.')
    widget = get_widget('.'.join(fullpath))
    return getattr(widget, attr_name)


def set_widget_attr(widget_attr_path, value):
    *fullpath, attr_name = widget_attr_path.split('.')
    widget = get_widget('.'.join(fullpath))
    setattr(widget, attr_name, value)


class BYONDWidget:
    base_pos = QtCore.QPoint(-1, -1)
    child_id_2_widget = {}

    def __init__(self, *args, **kwargs):
        self.id = kwargs.pop('id') if 'id' in kwargs else None
        
        self.parent_widget = args[0] if args else None
        
        if self.id:
            widget_id_2_widget[self.id] = self
            if self.parent_widget:
                self.parent_widget.child_id_2_widget[self.id] = self            
            
        super().__init__(*args, **kwargs)
        print(self.id)
        self.anchor_1 = None
        self.anchor_2 = None

    @property
    def is_visible(self):
        return self.isVisible()
        
    @is_visible.setter
    def is_visible(self, value):
        if value:
            self.show()
        else:
            self.hide()

    def setParent(self, parent):
        super().setParent(parent)
        if not self.id:
            return
        
        if self.parent_widget:
            del self.parent_widget.child_id_2_widget[self.id]
            
        self.parent_widget = parent
        self.parent_widget.child_id_2_widget[self.id] = self

        print("setParent", parent)

    def onShowEvent(self):
        pass

    def onHideEvent(self):
        pass

    def setAnchor1(self, *args):
        if len(args) == 1:
            self.anchor_1, = args
        else:
            x, y = args
            self.anchor_1 = QtCore.QPointF(x/100, y/100)

    def setAnchor2(self, *args):
        if len(args) == 1:
            self.anchor_2, = args
        else:
            x, y = args
            self.anchor_2 = QtCore.QPointF(x/100, y/100)

    def windowResizeEvent(self, QResizeEvent):
        if not QResizeEvent.oldSize() == NULL_SIZE:
            w_size = QResizeEvent.size()
            w_width, w_height = w_size.width(), w_size.height()

            wb_size = window.baseSize()
            wb_width, wb_height = wb_size.width(), wb_size.height()

            # width_ratio = w_width / wb_width
            # height_ratio = w_height / wb_height
            width_offset = w_width - wb_width
            height_offset = w_height - wb_height

            size = self.baseSize()
            width, height = size.width(), size.height()

            pos = self.basePos()
            x, y = pos.x(), pos.y()

            x2, y2 = x + width, y + height

            if self.anchor_1:
                x += width_offset * self.anchor_1.x()
                y += height_offset * self.anchor_1.y()

            if self.anchor_2:
                x2 += width_offset * self.anchor_2.x()
                y2 += height_offset * self.anchor_2.y()
                width = x2 - x
                height = y2 - y

            self.setGeometry(QtCore.QRect(x, y, width, height))
            print("QPushButton.windowResizeEvent {}, {}".format(w_width, w_height))
        else:
            print("INITIAL")

    def setBaseGeometry(self, *args):
        if len(args) == 1:
            rect = args[0]
            x, y, width, height = rect.x(), rect.y(), rect.width(), rect.height()
        else:
            x, y, width, height = args
        self.setBaseSize(width, height)
        self.setBasePos(x, y)
        print("QPushButton.setBaseGeometry")
        self.setGeometry(*args)

    def basePos(self):
        return self.base_pos

    def setBasePos(self, x, y):
        self.base_pos = QtCore.QPoint(x, y)


class QMainWindow(QtWidgets.QMainWindow):
    resized = QtCore.pyqtSignal(QtGui.QResizeEvent)
    child_id_2_widget = {}

    def resizeEvent(self, QResizeEvent):
        super().resizeEvent(QResizeEvent)
        self.resized.emit(QResizeEvent)
        print("QMainWindow.resizeEvent")

    def setBaseSize(self, *args):
        super().setBaseSize(*args)
        self.resize(*args)
        print("QMainWindow.setBaseSize")


class PushButton(BYONDWidget, QtWidgets.QPushButton):
    pass

class Input(BYONDWidget, QtWidgets.QLineEdit):
    pass

class Child(BYONDWidget, QtWidgets.QSplitter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._left = None
        self._right = None
    
    @property
    def left(self):
        return self._left
    
    @left.setter
    def left(self, widget):
        if widget and isinstance(widget, str):
            widget = widget_id_2_widget[widget]
    
        if self._left and self.indexOf(self._left):
            self._left.setParent(None)
        
        if widget:
            self.insertWidget(0, widget)
        
        self._left = widget
    
    @property
    def right(self):
        return self._right
    
    @right.setter
    def right(self, widget):
        if widget and isinstance(widget, str):
            widget = widget_id_2_widget[widget]
    
        if self._right and self.indexOf(self._right):
            self._right.setParent(None)
        
        if widget:    
            self.addWidget(widget)
        
        self._right = widget

class Pane(BYONDWidget, QtWidgets.QWidget):
    pass
    
class Output(BYONDWidget, QtWidgets.QTextBrowser):
    pass

class Browser(BYONDWidget, QtWidgets.QWidget):
    def showEvent(self, *args, **kwargs):
        super().showEvent(*args, **kwargs)
        self.onShowEvent()
        print("Browser.showEvent")

    def hideEvent(self, *args, **kwargs):
        super().hideEvent(*args, **kwargs)
        self.onHideEvent()
        print("Browser.hideEvent")


class Map(BYONDWidget, QtWidgets.QWidget):
    def showEvent(self, *args, **kwargs):
        super().showEvent(*args, **kwargs)
        self.onShowEvent()
        print("Map.showEvent")

    def hideEvent(self, *args, **kwargs):
        super().hideEvent(*args, **kwargs)
        self.onHideEvent()
        print("Map.hideEvent")


class Info(BYONDWidget, QtWidgets.QWidget):
    def showEvent(self, *args, **kwargs):
        super().showEvent(*args, **kwargs)
        self.onShowEvent()
        print("Info.showEvent")

    def hideEvent(self, *args, **kwargs):
        super().hideEvent(*args, **kwargs)
        self.onHideEvent()
        print("Info.hideEvent")

class Ui_MainWindow:
    def setupUi(self, MainWindow):
        self.mainWindow = MainWindow
        self.mainWindow.setWindowTitle("Dream Seeker")
        self.mainWindow.setBaseSize(640, 479)
        self.centralWidget = Pane(self.mainWindow, id="mainwindow")
        self.mainWindow.setCentralWidget(self.centralWidget)
        
        self.statusBar = QtWidgets.QStatusBar(self.mainWindow)
        self.statusBar.showMessage("water")
        self.statusBar.setFixedHeight(15)
        self.mainWindow.setStatusBar(self.statusBar)
        
        self.menuBar = QtWidgets.QMenuBar(self.mainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 640, 21))
        self.menuBar.setObjectName("menuBar")
        self.mainWindow.setMenuBar(self.menuBar)
        
        self.sizeGroup = QtWidgets.QActionGroup(self.mainWindow)
        
        self.menuFile = QtWidgets.QMenu(self.menuBar)
        self.menuFile.setObjectName("menuFile")
        self.menuFile.setTitle("&File")
        self.menuBar.addAction(self.menuFile.menuAction())
        
        self.actionOptions_and_messages = QtWidgets.QAction(self.menuFile)
        self.actionOptions_and_messages.setObjectName("actionOptions_and_messages")
        self.actionOptions_and_messages.setText("&Options and Messages...\tF1")
        self.menuFile.addAction(self.actionOptions_and_messages)
        
        self.actionQuick_screenshot = QtWidgets.QAction(self.menuFile)
        self.actionQuick_screenshot.setObjectName("actionQuick_screenshot")
        self.actionQuick_screenshot.setText("&Quick screenshot\tF2")
        self.menuFile.addAction(self.actionQuick_screenshot)
        
        self.actionSave_screenshot_as = QtWidgets.QAction(self.menuFile)
        self.actionSave_screenshot_as.setObjectName("actionSave_screenshot_as")
        self.actionSave_screenshot_as.setText("&Save screenshot as...\tShift+F2")
        self.menuFile.addAction(self.actionSave_screenshot_as)
        
        self.actionQuit = QtWidgets.QAction(self.menuFile)
        self.actionQuit.setObjectName("actionQuit")
        self.actionQuit.setText("&Quit")
        self.menuFile.addAction(self.actionQuit)
        
        self.menuIcons = QtWidgets.QMenu(self.menuBar)
        self.menuIcons.setObjectName("menuIcons")
        self.menuIcons.setTitle("&Icons")
        self.menuBar.addAction(self.menuIcons.menuAction())
        
        self.actionStretch = QtWidgets.QAction(self.sizeGroup)
        self.actionStretch.setObjectName("actionStretch")
        self.actionStretch.setText("&Stretch to fit")
        self.actionStretch.setCheckable(True)
        self.actionStretch.setChecked(True)
        self.menuIcons.addAction(self.actionStretch)
        
        self.actionIcon32 = QtWidgets.QAction(self.sizeGroup)
        self.actionIcon32.setObjectName("actionIcon32")
        self.actionIcon32.setText("&32x32")
        self.actionIcon32.setCheckable(True)
        self.menuIcons.addAction(self.actionIcon32)
        
        self.actionIcon16 = QtWidgets.QAction(self.sizeGroup)
        self.actionIcon16.setObjectName("actionIcon16")
        self.actionIcon16.setText("&16x16")
        self.actionIcon16.setCheckable(True)
        self.menuIcons.addAction(self.actionIcon16)
        
        self.menuIcons.addSeparator()
        
        self.actionTextmode = QtWidgets.QAction(self.menuIcons)
        self.actionTextmode.setObjectName("actionTextmode")
        self.actionTextmode.setText("&Text")
        self.actionTextmode.setCheckable(True)
        self.menuIcons.addAction(self.actionTextmode)
        
        self.mainvsplit = Child(self.centralWidget, id="mainvsplit")
        self.mainvsplit.setAnchor1(0, 0)
        self.mainvsplit.setAnchor2(100, 100)
        self.mainvsplit.setBaseGeometry(3, 0, 634, 400)
        self.mainvsplit.setObjectName("mainvsplit")
        self.mainWindow.resized.connect(self.mainvsplit.windowResizeEvent)
        self.mainvsplit.setOrientation(QtCore.Qt.Vertical)
        self.mainvsplit.setOpaqueResize(True)
        self.mainvsplit.setChildrenCollapsible(True)
        self.mainvsplit.setAutoFillBackground(True)
        palette = self.mainvsplit.palette()
        palette.setColor(self.mainvsplit.backgroundRole(), QtCore.Qt.red)
        self.mainvsplit.setPalette(palette)
        
        self.input = Input(self.centralWidget, id="input")
        self.input.setAnchor1(0, 100)
        self.input.setAnchor2(100, 100)
        self.input.setBaseGeometry(3, 420, 517, 20)
        self.input.setObjectName("input")
        self.mainWindow.resized.connect(self.input.windowResizeEvent)
        
        self.saybutton = PushButton(self.centralWidget, id="saybutton")
        self.saybutton.setCheckable(True)
        self.saybutton.setText("Chat")
        self.saybutton.setAnchor1(100, 100)
        self.saybutton.setBaseGeometry(520, 420, 40, 20)
        self.saybutton.setObjectName("saybutton")
        self.mainWindow.resized.connect(self.saybutton.windowResizeEvent)
        
        self.macrobutton = PushButton(self.centralWidget, id="macrobutton")
        self.macrobutton.setCheckable(True)
        self.macrobutton.setText("Alt")
        self.macrobutton.setAnchor1(100, 100)
        self.macrobutton.setBaseGeometry(560, 420, 30, 20)
        self.macrobutton.setObjectName("macrobutton")
        self.mainWindow.resized.connect(self.macrobutton.windowResizeEvent)
        
        self.hostb = PushButton(self.centralWidget, id="hostb")
        self.hostb.setText("Host...")
        self.hostb.setAnchor1(100, 100)
        self.hostb.setBaseGeometry(590, 420, 47, 20)
        self.hostb.setObjectName("hostb")
        self.mainWindow.resized.connect(self.hostb.windowResizeEvent)
        
        self.mapwindow = Pane(id="mapwindow")
        self.mapwindow.setBaseGeometry(0, 0, 640, 480)
        self.mapwindow.setObjectName("mapwindow")
        
        self.map = Map(self.mapwindow, id="map")
        self.map.setAnchor1(0, 0)
        self.map.setAnchor2(100, 100)
        self.map.setBaseGeometry(0, 0, 0, 0)
        self.map.setObjectName("map")
        self.mainWindow.resized.connect(self.map.windowResizeEvent)
        
        def on_show():
            set_widget_attr("mainwindow.mainvsplit.left", "mapwindow")
        
        self.map.onShow = on_show
        
        def on_hide():
            set_widget_attr("mainwindow.mainvsplit.left", "")
        
        self.map.onHide = on_hide
        self.map.setAutoFillBackground(True)
        palette = self.map.palette()
        palette.setColor(self.map.backgroundRole(), QtCore.Qt.black)
        self.map.setPalette(palette)
        self.mapwindow.setAutoFillBackground(True)
        palette = self.mapwindow.palette()
        palette.setColor(self.mapwindow.backgroundRole(), QtCore.Qt.green)
        self.mapwindow.setPalette(palette)
        
        self.outputwindow = Pane(id="outputwindow")
        self.outputwindow.setBaseGeometry(0, 0, 640, 480)
        self.outputwindow.setObjectName("outputwindow")
        
        self.output = Output(self.outputwindow, id="output")
        self.output.setAnchor1(0, 0)
        self.output.setAnchor2(100, 100)
        self.output.setBaseGeometry(0, 0, 0, 0)
        self.output.setObjectName("output")
        self.mainWindow.resized.connect(self.output.windowResizeEvent)
        self.outputwindow.setAutoFillBackground(True)
        palette = self.outputwindow.palette()
        palette.setColor(self.outputwindow.backgroundRole(), QtCore.Qt.green)
        self.outputwindow.setPalette(palette)
        
        self.rpane = Pane(id="rpane")
        self.rpane.setBaseGeometry(0, 0, 640, 480)
        self.rpane.setObjectName("rpane")
        
        self.rpanewindow = Child(self.rpane, id="rpanewindow")
        self.rpanewindow.setAnchor1(0, 0)
        self.rpanewindow.setAnchor2(100, 100)
        self.rpanewindow.setBaseGeometry(0, 0, 0, 0)
        self.rpanewindow.setObjectName("rpanewindow")
        self.mainWindow.resized.connect(self.rpanewindow.windowResizeEvent)
        self.rpanewindow.setOrientation(QtCore.Qt.Horizontal)
        self.rpanewindow.setOpaqueResize(True)
        self.rpanewindow.setChildrenCollapsible(True)
        self.rpanewindow.setAutoFillBackground(True)
        palette = self.rpanewindow.palette()
        palette.setColor(self.rpanewindow.backgroundRole(), QtCore.Qt.red)
        self.rpanewindow.setPalette(palette)
        
        self.textb = PushButton(self.rpane, id="textb")
        self.textb.setCheckable(True)
        self.textb.setChecked(True)
        self.textb.setText("Text")
        self.textb.setBaseGeometry(0, 0, 60, 20)
        self.textb.setObjectName("textb")
        
        self.browseb = PushButton(self.rpane, id="browseb")
        self.browseb.setCheckable(True)
        self.browseb.setText("Browser")
        self.browseb.setBaseGeometry(65, 0, 60, 20)
        self.browseb.setObjectName("browseb")
        
        self.infob = PushButton(self.rpane, id="infob")
        self.infob.setCheckable(True)
        self.infob.setText("Info")
        self.infob.setBaseGeometry(130, 0, 60, 20)
        self.infob.setObjectName("infob")
        self.rpane.setAutoFillBackground(True)
        palette = self.rpane.palette()
        palette.setColor(self.rpane.backgroundRole(), QtCore.Qt.green)
        self.rpane.setPalette(palette)
        
        self.browserwindow = Pane(id="browserwindow")
        self.browserwindow.setBaseGeometry(0, 0, 640, 480)
        self.browserwindow.setObjectName("browserwindow")
        
        self.browser = Browser(self.browserwindow, id="browser")
        self.browser.setAnchor1(0, 0)
        self.browser.setAnchor2(100, 100)
        self.browser.setBaseGeometry(0, 0, 0, 0)
        self.browser.setObjectName("browser")
        self.mainWindow.resized.connect(self.browser.windowResizeEvent)
        
        def on_show():
            if get_widget_attr("rpane.infob.is_visible") == True:
                set_widget_attr("rpane.infob.pos", (130, 0))
            set_widget_attr("rpane.textb.is_visible", True)
            set_widget_attr("rpane.browseb.is_visible", True)
            set_widget_attr("rpane.browseb.is_checked", True)
            set_widget_attr("rpane.rpanewindow.pos", (0, 30))
            set_widget_attr("rpane.rpanewindow.size", (0, 0))
            set_widget_attr("rpane.rpanewindow.left", "browserwindow")
        
        self.browser.onShow = on_show
        
        def on_hide():
            set_widget_attr("rpane.browseb.is_visible", False)
            if get_widget_attr("rpane.infob.is_visible") == True:
                set_widget_attr("rpane.infob.is_checked", True)
                set_widget_attr("rpane.infob.pos", (65, 0))
                set_widget_attr("rpane.rpanewindow.left", "infowindow")
            else:
                set_widget_attr("rpane.rpanewindow.left", "textwindow")
                set_widget_attr("rpane.textb.is_visible", False)
                set_widget_attr("rpane.rpanewindow.pos", (0, 0))
                set_widget_attr("rpane.rpanewindow.size", (0, 0))
        
        self.browser.onHide = on_hide
        self.browser.setAutoFillBackground(True)
        palette = self.browser.palette()
        palette.setColor(self.browser.backgroundRole(), QtCore.Qt.yellow)
        self.browser.setPalette(palette)
        self.browserwindow.setAutoFillBackground(True)
        palette = self.browserwindow.palette()
        palette.setColor(self.browserwindow.backgroundRole(), QtCore.Qt.green)
        self.browserwindow.setPalette(palette)
        
        self.infowindow = Pane(id="infowindow")
        self.infowindow.setBaseGeometry(0, 0, 640, 480)
        self.infowindow.setObjectName("infowindow")
        
        self.info = Info(self.infowindow, id="info")
        self.info.setAnchor1(0, 0)
        self.info.setAnchor2(100, 100)
        self.info.setBaseGeometry(0, 0, 0, 0)
        self.info.setObjectName("info")
        self.mainWindow.resized.connect(self.info.windowResizeEvent)
        
        def on_show():
            set_widget_attr("rpane.infob.is_visible", True)
            if get_widget_attr("rpane.browseb.is_visible") == True:
                set_widget_attr("rpane.infob.pos", (130, 0))
            else:
                set_widget_attr("rpane.infob.pos", (65, 0))
                set_widget_attr("rpane.textb.is_visible", True)
                set_widget_attr("rpane.infob.is_checked", True)
                set_widget_attr("rpane.rpanewindow.pos", (0, 30))
                set_widget_attr("rpane.rpanewindow.size", (0, 0))
                set_widget_attr("rpane.rpanewindow.left", "infowindow")
        
        self.info.onShow = on_show
        
        def on_hide():
            set_widget_attr("rpane.infob.is_visible", False)
            if get_widget_attr("rpane.browseb.is_visible") == True:
                set_widget_attr("rpane.browseb.is_checked", True)
                set_widget_attr("rpane.rpanewindow.left", "browserwindow")
            else:
                set_widget_attr("rpane.textb.is_visible", False)
                set_widget_attr("rpane.rpanewindow.pos", (0, 0))
                set_widget_attr("rpane.rpanewindow.size", (0, 0))
                set_widget_attr("rpane.rpanewindow.left", "")
        
        self.info.onHide = on_hide
        self.info.setAutoFillBackground(True)
        palette = self.info.palette()
        palette.setColor(self.info.backgroundRole(), QtCore.Qt.darkBlue)
        self.info.setPalette(palette)
        self.infowindow.setAutoFillBackground(True)
        palette = self.infowindow.palette()
        palette.setColor(self.infowindow.backgroundRole(), QtCore.Qt.green)
        self.infowindow.setPalette(palette)

        self.mainvsplit.right = get_widget("rpane")
        
        self.rpanewindow.right = get_widget("outputwindow")

        self.map.onShow()
        self.info.onHide()
        self.browser.onShow()
        # self.mainvsplit.left = self.mapwindow
        # self.mainvsplit.insertWidget(0, self.map)
        # self.map.setParent(self.mainvsplit)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('GTK+'))
    window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec_())
