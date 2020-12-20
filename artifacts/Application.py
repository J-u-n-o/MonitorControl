
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QAbstractNativeEventFilter
import datetime
import ctypes
import time
import os

import SingleApplication
import Handles
import Identify
import TrayWindow
import MonitorObserver
import threading
import pythoncom

RUN_PATH = "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
ACCENT_PATH = r'HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Accent'
THEME_PATH = "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize"

appGuid = 'B0EFFF-B0EF-B0EF-B0EF-B0EFB0EFB0EF'


class Application(SingleApplication.SingleApplication):

    textColor = QtGui.QColor('black')
    backgroundColor = QtGui.QColor(30, 30, 30)
    darkColor = None
    tabColor = None

    def cleanUp(self):
        now = datetime.datetime.now()
        print("{} Closing".format(now.strftime("%H:%M:%S")))
        self.monitors_stop()

    def __init__(self, argv):
        # super(QApplication, self).__init__(argv)
        super().__init__(appGuid, argv)

        print("Application init")

        if (self.isRunning()):
            print("Application already running")
            super().exit()
            return

        self.win_event_filter = WinEventFilter(self, "app")
        self.installNativeEventFilter(self.win_event_filter)

        self.aboutToQuit.connect(self.cleanUp)

        self.settings = QtCore.QSettings(
            THEME_PATH, QtCore.QSettings.NativeFormat)
        print(self.settings)
        print(self.settings.contains("AppsUseLightTheme"))
        print(self.settings.value("AppsUseLightTheme"))
        # print(QStyleFactory.keys())
        if (self.settings.contains("AppsUseLightTheme") and (self.settings.value("AppsUseLightTheme") == 0)):
            self.setStyle("Fusion")
            textColor = QtGui.QColor('white')

            darkPalette = QtGui.QPalette()
            Application.darkColor = QtGui.QColor(30, 30, 30)
            Application.tabColor = QtGui.QColor(0x27, 0x27, 0x27)
            disabledColor = QtGui.QColor(127, 127, 127)
            accentColor = QtGui.QColor(42, 130, 218)
            accentColor = Application.getAccentColor()
            print('darkPalette {}'.format(type(darkPalette)))
            print('QtGui.QPalette.Window {}'.format(
                type(QtGui.QPalette.Window)))
            print('darkColor {}'.format(type(Application.darkColor)))
            darkPalette.setColor(QtGui.QPalette.Window, Application.darkColor)
            darkPalette.setColor(QtGui.QPalette.WindowText,
                                 QtGui.QColor('white'))
            darkPalette.setColor(QtGui.QPalette.Base, QtGui.QColor(18, 18, 18))
            darkPalette.setColor(
                QtGui.QPalette.AlternateBase, Application.darkColor)
            darkPalette.setColor(
                QtGui.QPalette.ToolTipBase, QtGui.QColor('white'))
            darkPalette.setColor(
                QtGui.QPalette.ToolTipText, QtGui.QColor('white'))
            darkPalette.setColor(QtGui.QPalette.Text, QtGui.QColor('white'))
            darkPalette.setColor(QtGui.QPalette.Disabled,
                                 QtGui.QPalette.Text, disabledColor)
            darkPalette.setColor(QtGui.QPalette.Button, Application.darkColor)
            darkPalette.setColor(QtGui.QPalette.ButtonText,
                                 QtGui.QColor('white'))
            darkPalette.setColor(QtGui.QPalette.Disabled,
                                 QtGui.QPalette.ButtonText, disabledColor)
            darkPalette.setColor(
                QtGui.QPalette.BrightText, QtGui.QColor('red'))
            darkPalette.setColor(QtGui.QPalette.Link,
                                 accentColor)

            darkPalette.setColor(QtGui.QPalette.Highlight,
                                 accentColor)
            darkPalette.setColor(
                QtGui.QPalette.HighlightedText, QtGui.QColor('black'))
            darkPalette.setColor(QtGui.QPalette.Disabled,
                                 QtGui.QPalette.HighlightedText, disabledColor)

            Application.textColor = textColor
            Application.backgroundColor = Application.darkColor

            self.setPalette(darkPalette)

            self.setStyleSheet("QToolTip {color: #ffffff; background-color: #2a82da; border: 1px solid white; }"
                               "QMenu::item:checked {background-color: #2a82da; }")

        settings = QtCore.QSettings(RUN_PATH, QtCore.QSettings.NativeFormat)
        self.window = None
        self.observe_timer = None
        self.monitors = None
        self.identifyWindows = []

    def create_start_monitors(self):

        self.identifyWindows = []
        self.window = TrayWindow.Window(self)
        self.setActivationWindow(self.window)

        self.monitors = MonitorObserver.Monitors()
        self.monitors.add_observer(self)

        print("Application detect_monitors")
        self.monitors_start()

        self.window.position_show()

        self.window.hide()

        # setup stylesheet
        # the default system in qdarkstyle uses qtpy environment variable
        # app.setStyleSheet(qdarkstyle.load_stylesheet())

    def notify(self, obj, event):
        if event.type() == QtCore.QEvent.WindowDeactivate:
            # print("{} was deactivated =?= {}".format(obj, self.window))
            if (obj == self.window) and (len(self.identifyWindows) == 0):
                print("{} was deactivated == {}".format(obj, self.window))
                self.window.hide()

        if event.type() == QtCore.QEvent.WindowActivate:
            if (obj == self.window):
                print("{} was activated. {}".format(obj, self.window))
        return super().notify(obj, event)


# https://stackoverflow.com/questions/58927021/how-to-display-image-on-secondary-monitor-in-full-screen

    def position_next_to_tray(self):

        screen = self.primaryScreen()
        print('Screen: %s' % screen.name())
        size = screen.size()
        print('Size: %d x %d %d, %d' % (size.width(), size.height(),
                                        screen.geometry().x(), screen.geometry().y()))
        screen_rect = screen.geometry()
        available_screen_rect = screen.availableGeometry()
        screen_size = screen.size()
        print('Available: %d x %d %d, %d' %
              (available_screen_rect.width(), available_screen_rect.height(), available_screen_rect.x(), available_screen_rect.y()))
        print('Screen: %d x %d %d, %d' %
              (screen_rect.width(), screen_rect.height(), screen_rect.x(), screen_rect.y()))

        window_size = self.window.size()
        print('Window size: %d x %d' %
              (window_size.width(), window_size.height()))
        self.window.window_position = QtCore.QPoint(
            available_screen_rect.x(),
            available_screen_rect.y())
        self.window.window_position_offset = QtCore.QPoint(0, 0)
        print('Window pos: %d, %d' %
              (self.window.window_position.x(), self.window.window_position.y()))

        if (available_screen_rect.x() > screen_rect.x()):
            # left
            print("left")
            self.window.window_position = QtCore.QPoint(
                available_screen_rect.x(),
                (available_screen_rect.y() +
                 available_screen_rect.height()) - self.window.window_size.height())
            self.window.window_position_offset = QtCore.QPoint(
                0, -self.window.window_size_offset.height())
        elif ((available_screen_rect.x() + available_screen_rect.width()) < (screen_rect.x() + screen_rect.width())):
            # right
            print("right")
            self.window.window_position = QtCore.QPoint(
                (available_screen_rect.x() +
                 available_screen_rect.width()) - self.window.window_size.width(),
                (available_screen_rect.y() +
                    available_screen_rect.height()) - self.window.window_size.height())
            self.window.window_position_offset = QtCore.QPoint(
                0, -self.window.window_size_offset.height())
        else:
            if (available_screen_rect.y() > screen_rect.y()):
                # top
                print("top")
                self.window.window_position = QtCore.QPoint(
                    available_screen_rect.x(),
                    (available_screen_rect.y() +
                        available_screen_rect.height()) - self.window.window_size.height())
                self.window.window_position_offset = QtCore.QPoint(0, 0)

            elif ((available_screen_rect.y() + available_screen_rect.height()) < (screen_rect.y() + screen_rect.height())):
                # bottom
                print("bottom")
                self.window.window_position = QtCore.QPoint(
                    (available_screen_rect.x() +
                     available_screen_rect.width()) - window_size.width(),
                    (available_screen_rect.y() +
                     available_screen_rect.height()) - window_size.height())
                self.window.window_position_offset = QtCore.QPoint(
                    0, -self.window.window_size_offset.height())
            else:
                x = 1
                print("none")

        print('Window pos: %d, %d' %
              (self.window.window_position.x(), self.window.window_position.y()))
        self.window.move(self.window.window_position)
        self.window.resize(self.window.window_size)

    @staticmethod
    def getAccentColor():
        """
        Return the Windows 10 accent color used by the user in a HEX format
        """
        # Open the registry
        settings = QtCore.QSettings(ACCENT_PATH, QtCore.QSettings.NativeFormat)
        print(settings)
        key = "StartColorMenu"
        key = "AccentColorMenu"
        print(settings.contains(key))
        print(settings.value(key))

        accent_int = settings.value(key)
        # Remove FF offset and convert to HEX again
        accent_hex = hex(accent_int+4278190080)
        print(accent_hex)
        accent_hex = str(accent_hex)[4:-1]  # Remove prefix and suffix
        # The HEX value was originally in a BGR order, instead of RGB,
        # so we reverse it...
        accent = accent_hex[4:6]+accent_hex[2:4]+accent_hex[0:2]

        return QtGui.QColor(int(accent_hex[4:6], 16), int(accent_hex[2:4], 16), int(accent_hex[0:2], 16))

    def detect_monitors(self):
        self.monitors.detect_monitors()

    def brightness(self, value):
        # from gui
        self.monitors.set_brightness(value)

    def contrast(self, value):
        # from gui
        self.monitors.set_contrast(value)

    def set_contrast(self, value):
        # to gui
        self.window.set_contrast(value)

    def set_brightness(self, value):
        # to gui
        self.window.set_brightness(value)

    def observe(self):
        self.observe_timer = threading.Timer(1.0, self.observe)

        self.observe_timer.start()
        # print("monitors.tick()")
        pythoncom.CoInitialize()
        self.monitors.tick()

        print(f"{time.ctime()}, {Handles.getGDIcount(os.getpid())}")

    def closeEvent(self, event):
        print(" quit")
        self.monitors_stop()

    def me_exit(self):
        print(" app exit")
        self.monitors_stop()
        self.window.close()
        super().exit()

    def monitors_stop(self):
        print("Application monitors_stop")
        if (self.window is not None):
            self.window.hide()
        if (self.observe_timer is not None):
            self.observe_timer.cancel()
        if (self.monitors is not None):
            self.monitors.remove_displays()

    def monitors_start(self):
        print("Application monitors_start")
        self.detect_monitors()

        self.observe()

    def restore_deactivation(self, window):
        print("Application restore_deactivation")
        if (self.window.isVisible()):
            self.window.activateWindow()
            self.window.setFocus(QtCore.Qt.PopupFocusReason)
        print("Application restore_deactivation {}".format(self.identifyWindows))
        self.identifyWindows.remove(window)

    def identify(self):
        print("Identify {}".format(len(self.identifyWindows)))
        if (len(self.identifyWindows) == 0):
            index = 0
            print('monitors._monitor_observers')
            for _monitor_observer in self.monitors._monitor_observers:
                print('monitors._monitor_observers a {}'.format(
                    type(_monitor_observer)))
                if (type(_monitor_observer) == MonitorObserver.MonitorObserver):
                    print('monitors._monitor_observers b {} {}'.format(
                        type(_monitor_observer._monitor._rect), _monitor_observer._monitor._rect))
                    self.identifyWindows.append(Identify.IdentifyWindow(
                        index, QtCore.QRect(_monitor_observer._monitor._rect[0],
                                            _monitor_observer._monitor._rect[1],
                                            _monitor_observer._monitor._rect[2] -
                                            _monitor_observer._monitor._rect[0],
                                            _monitor_observer._monitor._rect[3] - _monitor_observer._monitor._rect[1]), self.window, self.restore_deactivation))
                    index += 1

            print('windows {}'.format(len(self.identifyWindows)))
            for window in self.identifyWindows:
                print('  window show {}'.format(str(window)))
                window.show()


class WinEventFilter(QAbstractNativeEventFilter):
    def __init__(self, app, name):
        QAbstractNativeEventFilter.__init__(self)
        self.app = app
        self.name = name

    def nativeEventFilter(self, eventType, message):
        msg = ctypes.wintypes.MSG.from_address(message.__int__())
        now = datetime.datetime.now()
        if msg.message == 0x0219:  # WM_DEVICECHANGE
            print("{} {} Message1 Received! WM_DEVICECHANGE".format(self.name,
                                                                    now.strftime("%H:%M:%S")))
            if msg.wParam == 0x8000:  # DBT_DEVICEARRIVAL
                print("in")
            elif msg.wParam == 0x8004:  # DBT_DEVICEREMOVECOMPLETE
                print("out")
            elif msg.wParam == 0x0007:  # DBT_DEVNODE_CHANGED
                print("node")
        elif msg.message == 0x0218:  # WM_POWERBROADCAST
            print("{} {} Message1 Received! WM_POWERBROADCAST".format(self.name,
                                                                      now.strftime("%H:%M:%S")))
            if msg.wParam == 0x000A:  # PBT_APMPOWERSTATUSCHANGE
                print(" PBT_APMPOWERSTATUSCHANGE")
            elif msg.wParam == 0x0012:  # PBT_APMRESUMEAUTOMATIC
                print("  PBT_APMRESUMEAUTOMATIC")
                self.app.monitors_start()
            elif msg.wParam == 0x0007:  # PBT_APMRESUMESUSPEND
                print("  PBT_APMRESUMESUSPEND")
                self.app.monitors_start()
            elif msg.wParam == 0x0004:  # PBT_APMSUSPEND
                print("  PBT_APMSUSPEND")
                self.app.monitors_stop()
            elif msg.wParam == 0x8013:  # PBT_POWERSETTINGCHANGE
                print("  PBT_POWERSETTINGCHANGE")
            else:
                print("  {}".format(msg.wParam))

        elif msg.message == 0x007E:
            print("{} {} Message1 Received! WM_DISPLAYCHANGE".format(self.name,
                                                                     now.strftime("%H:%M:%S")))
            self.app.monitors_start()
        elif msg.message == 0x0016:
            print("{} {} Message1 Received! WM_ENDSESSION".format(self.name,
                                                                  now.strftime("%H:%M:%S")))
        elif eventType == "{} windows_generic_MSG":
            # WM_DISPLAYCHANGE = 0x7E
            print("{} {} windows_generic_MSG {}".format(self.name,
                                                        now.strftime("%H:%M:%S"), msg.message))
            if msg.message == 0x7E:
                print("{} Message2 Received! WM_DISPLAYCHANGE".format(
                    now.strftime("%H:%M:%S")))

        return False, 0
