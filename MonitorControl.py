from artifacts import ExtendPythonPath
from artifacts import GotoParentFolder

import winreg
import pythoncom
import threading
import os
from os import path
import sys
from PySide2 import QtWidgets, QtCore, QtGui
import TrayWindow
import Application


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):

    def __init__(self, app, icon, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, app)

        self.app = app
        self._parent = parent

        self.update_menu()

        print("SystemTrayIcon init")
        self.activated.connect(self.systemIcon)
        print("SystemTrayIcon activated")

    def update_menu(self):
        menu = QtWidgets.QMenu(self._parent)
        prefs_action = menu.addAction('Show...')
        menu.addSeparator()
        if (IsInRegistry()):
            startup_action = menu.addAction('Stop running at startup')
        else:
            startup_action = menu.addAction('Run at startup')
        menu.addSeparator()
        quit_action = menu.addAction('Exit')

        self.setContextMenu(menu)
        startup_action.triggered.connect(self.setStartup)
        prefs_action.triggered.connect(self.setPrefs)

        quit_action.triggered.connect(self.setQuit)

    def setStartup(self):
        if (IsInRegistry()):
            RemoveFromRegistry()
        else:
            AddToRegistry()
        self.update_menu()

    def setPrefs(self):
        self.app.window.position_show()

    def setQuit(self):
        print("setQuit")
        self.app.monitors_stop()
        self.app.window.close()
        self.app.me_exit()
        # sys.exit()

    def systemIcon(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger:
            self.app.window.position_show()

            print('Clicked')
        else:
            print('systemIcon {}'.format(reason))


# Python code to add current script to the registry
# module to edit the windows registry


def AddToRegistry():

    # in python __file__ is the instant of
    # file path where it was executed
    # so if it was executed from desktop,
    # then __file__ will be
    # c:\users\current_user\desktop
    pth = os.path.dirname(os.path.realpath(__file__))

    # name of the python file with extension
    s_name = "TrayApp.py"

    # joins the file name to end of path address
    address = os.path.join(pth, s_name)

    # key we want to change is HKEY_CURRENT_USER
    # key value is Software\Microsoft\Windows\CurrentVersion\Run
    key = winreg.HKEY_CURRENT_USER
    key_value = "Software\Microsoft\Windows\CurrentVersion\Run"

    # open the key to make changes to
    open = winreg.OpenKey(key, key_value, 0, winreg.KEY_ALL_ACCESS)

    # modifiy the opened key
    winreg.SetValueEx(open, "MonitorControl", 0, winreg.REG_SZ, address)

    # now close the opened key
    winreg.CloseKey(open)


def RemoveFromRegistry():

    # in python __file__ is the instant of
    # file path where it was executed
    # so if it was executed from desktop,
    # then __file__ will be
    # c:\users\current_user\desktop
    pth = os.path.dirname(os.path.realpath(__file__))

    # name of the python file with extension
    s_name = "TrayApp.py"

    # joins the file name to end of path address
    address = os.path.join(pth, s_name)

    # key we want to change is HKEY_CURRENT_USER
    # key value is Software\Microsoft\Windows\CurrentVersion\Run
    key = winreg.HKEY_CURRENT_USER
    key_value = "Software\Microsoft\Windows\CurrentVersion\Run"

    # open the key to make changes to
    open = winreg.OpenKey(key, key_value, 0, winreg.KEY_ALL_ACCESS)

    # modify the opened key
    winreg.DeleteValue(open, "MonitorControl", 0, winreg.REG_SZ, address)

    # now close the opened key
    winreg.CloseKey(open)


def IsInRegistry():
    present = False
    # in python __file__ is the instant of
    # file path where it was executed
    # so if it was executed from desktop,
    # then __file__ will be
    # c:\users\current_user\desktop
    pth = os.path.dirname(os.path.realpath(__file__))

    # name of the python file with extension
    s_name = "MonitorControl.py"

    # joins the file name to end of path address
    address = os.path.join(pth, s_name)

    # key we want to change is HKEY_CURRENT_USER
    # key value is Software\Microsoft\Windows\CurrentVersion\Run
    key = winreg.HKEY_CURRENT_USER
    key_value = "Software\Microsoft\Windows\CurrentVersion\Run"

    # open the key to make changes to
    open = winreg.OpenKey(key, key_value, 0, winreg.KEY_ALL_ACCESS)

    try:
        # modify the opened key
        winreg.QueryValueEx(open, "MonitorControl")
        present = True
    except FileNotFoundError:
        present = False

    # now close the opened key
    winreg.CloseKey(open)

    return present


def main(image):
    print('->app')
    app = Application.Application(sys.argv)

    if (app.isRunning()):
        exit()

    app.create_start_monitors()

    print('->w')
    w = QtWidgets.QWidget()
    print('->SystemTrayIcon')
    trayIcon = SystemTrayIcon(app, QtGui.QIcon(image), w)
    print('->Show')
    trayIcon.show()

    print('wait for main exit')
    sys.exit(app.exec_())


if __name__ == '__main__':
    print('->main')
    icon = 'artifacts/icon.png'
    main(icon)
