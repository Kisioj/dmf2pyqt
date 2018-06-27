TEMPLATE = '''#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication, QStyleFactory
from PyQt5 import QtCore, QtGui, QtWidgets

NULL_SIZE = QtCore.QSize(-1, -1)

SHOW_BROWSER = True
SHOW_INFO = True
SHOW_MAP = True

widget_id_2_widget = {{}}


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
    child_id_2_widget = {{}}

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
            print("QPushButton.windowResizeEvent {{}}, {{}}".format(w_width, w_height))
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
    child_id_2_widget = {{}}

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
{}

{}

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
'''