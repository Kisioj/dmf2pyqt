TEMPLATE = '''#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore, QtGui, QtWidgets

NULL_SIZE = QtCore.QSize(-1, -1)


class BYONDWidget:
    base_pos = QtCore.QPoint(-1, -1)

    def __init__(self, *args):
        # super().__init__(*args)
        self.anchor_1 = None
        self.anchor_2 = None

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

    def resizeEvent(self, QResizeEvent):
        super().resizeEvent(QResizeEvent)
        self.resized.emit(QResizeEvent)
        print("QMainWindow.resizeEvent")

    def setBaseSize(self, *args):
        super().setBaseSize(*args)
        self.resize(*args)
        print("QMainWindow.setBaseSize")


class PushButton(QtWidgets.QPushButton, BYONDWidget):
    pass

class Input(QtWidgets.QLineEdit, BYONDWidget):
    pass

class Child(QtWidgets.QWidget, BYONDWidget):
    pass

class Pane(QtWidgets.QWidget, BYONDWidget):
    pass

class Map(QtWidgets.QWidget, BYONDWidget):
    pass

class Ui_MainWindow:
    def setupUi(self, MainWindow):
{}
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec_())
'''