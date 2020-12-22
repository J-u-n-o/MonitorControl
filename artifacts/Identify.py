try:
    from artifacts import ExtendPythonPath
except Exception as err:
    # print(err)
    # traceback.print_exc()
    None


import datetime
import ctypes
from PySide2.QtCore import QAbstractNativeEventFilter
from pyqtgraph.Qt import QtCore, QtGui
import sys
import threading
import pythoncom
from PySide2 import (QtCore)
from PySide2 import (QtGui)
from PySide2 import (QtWidgets)
from PySide2.QtWidgets import *

# from PySide2.QtCore import (Qt, QSettings, pyqtSlot)

from PySide2.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox, QTabWidget,
                               QMenu, QPushButton, QRadioButton, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QStyleFactory)

import qdarkstyle
import os

import MonitorObserver
import MonitorDetect
import Application

import pyqtgraph

import signal
import Identify


# class IdentifyWindow(QWidget):
# class IdentifyWindow(QMainWindow):
class IdentifyWindow(QDialog):
    def __init__(self, index, screen_rect, parent, restore):
        super().__init__(parent=parent)
        self.restore = restore
        self.title = "Monitor {} identifier".format(index+1)
        self.screen_rect = screen_rect

        print(' {}: {} {} {}'.format(index, screen_rect,
                                     screen_rect.width(), screen_rect.height()))

        l = min(screen_rect.width(), screen_rect.height()) / 6
        self.width = 2 * l
        self.height = self.width
        self.top = screen_rect.top() + screen_rect.height() - 3 * l
        self.left = screen_rect.left() + l
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        print(' {}: {}, {}; {} x {}'.format(
            index, self.left, self.top, self.width, self.height))

        flags = QtCore.Qt.WindowFlags(
            QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        # self.setWindowFlags(flags)

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint)

        # self.button = QtGui.QPushButton('test', self)

        self.label = QtGui.QLabel('{}'.format(index + 1), self)
        # self.label = QtGui.QPushButton('{}'.format(index + 1), self)

        self.font = self.label.font()
        self.font.setBold(True)
        self.font.setPixelSize(1.6 * l)

        self.label.setFont(self.font)
        # self.label.setStyleSheet(
        #    "QLabel { background-color : red; color : blue; }")
        self.label.setStyleSheet(
            "QLabel { color : " + Application.Application.textColor.name() + "; }")
        self.label.setAutoFillBackground(True)

        self.layout = QVBoxLayout()
        # self.layout.addWidget(
        #    self.button)
        # self.label.setSizePolicy(QtGui.QSizePolicy.Maximum,
        #                         QtGui.QSizePolicy.Maximum)

        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.layout.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(
            self.label, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)
        self.setLayout(self.layout)

        self.resize(self.width+1, self.height)
        self.resize(self.width, self.height)
        self.move(self.left+1, self.top)
        self.move(self.left, self.top)

        self.layout.setGeometry(
            QtCore.QRect(0, 0, self.geometry().width(), self.geometry().height()))

        self.show()
        self.label.show()
        # self.button.show()

        self.current_timer = QtCore.QTimer()
        self.current_timer.timeout.connect(self.Close)
        self.current_timer.setSingleShot(True)
        self.current_timer.start(3000)

    def Close(self):
        print(' window {}'.format(
            self.frameGeometry()))
        print(' window2 {}'.format(
            self.geometry()))
        print(' label {}'.format(
            self.label.frameGeometry()))
        print(' layout {}'.format(
            self.label.geometry()))

        if (self.restore is not None):
            self.restore(self)

        print(' close {}'.format(self.title))

        self.close()
        # close seems not to destroy the QDialog, so do it ourself
        self.destroy()


def signal_handler(sig, frame):
    global application_running
    print('You pressed Ctrl+C!')
    sys.exit(0)


class Window(QWidget):
    def __init__(self, app, parent=None):

        print("Window init")

        super().__init__(parent)


def hallo(window):
    print('halle')


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    app = Application.Application(sys.argv)

    rect = QtCore.QRect(0, 0, 1920, 1200)

    main_window = Identify.Window(None)
    main_window.show()
    # main_window = None

    monitors = MonitorObserver.Monitors()
    monitors.detect_monitors()

    windows = []
    index = 0
    print('monitors._monitor_observers')
    for _monitor_observer in monitors._monitor_observers:
        print('monitors._monitor_observers a {}'.format(type(_monitor_observer)))
        if (type(_monitor_observer) == MonitorObserver.MonitorObserver):
            print('monitors._monitor_observers b {} {}'.format(
                type(_monitor_observer._monitor._rect), _monitor_observer._monitor._rect))
            windows.append(Identify.IdentifyWindow(
                index, QtCore.QRect(_monitor_observer._monitor._rect[0],
                                    _monitor_observer._monitor._rect[1],
                                    _monitor_observer._monitor._rect[2] -
                                    _monitor_observer._monitor._rect[0],
                                    _monitor_observer._monitor._rect[3] - _monitor_observer._monitor._rect[1]), main_window, hallo))
            index += 1

    print('windows {}'.format(len(windows)))
    for window in windows:
        print('  window  {}'.format(str(window)))
        window.show()

    print('wait')

    sys.exit(app.exec_())
