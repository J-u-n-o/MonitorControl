# pythonprogramminglanguage.com
import datetime
import ctypes
from pyqtgraph.Qt import QtCore, QtGui
import sys

from PySide2.QtCore import QAbstractNativeEventFilter, Qt
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

# from PySide2.QtCore import (Qt, QSettings, pyqtSlot)

from PySide2.QtWidgets import QGridLayout, QTabWidget, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QLabel, QSizePolicy, QApplication

import qdarkstyle
import os

import MonitorObserver
import MonitorDetect
import Identify
import CalibrationWidget
import Application
import Display
import Handles
import time

import pyqtgraph
pyqtgraph.setConfigOptions(antialias=True)


class Window(QWidget):
    def __init__(self, app, parent=None):

        print("Window init")

        super().__init__(parent)

        # self.win_event_filter = WinEventFilter("window")
        # self.installNativeEventFilter(self.win_event_filter)

        self.app = app

        self.window_size = QtCore.QSize(400, 200)
        self.window_size_offset = QtCore.QSize(0, 150)
        self.window_position = QtCore.QPoint(0, 0)
        self.window_position_offset = QtCore.QPoint(0, 0)

        # self.setWindowFlags(
        #    QtCore.Qt.Window |
        #    QtCore.Qt.CustomizeWindowHint |
        #    QtCore.Qt.WindowTitleHint |
        #    QtCore.Qt.WindowCloseButtonHint |
        #    QtCore.Qt.WindowStaysOnTopHint
        # )

        self.setWindowFlags(self.windowFlags() |
                            QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(self.windowFlags() |
                            QtCore.Qt.WindowStaysOnTopHint)

        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool)
        # hlayout = QHBoxLayout()
        # hlayout.setMargin(0)
        # hlayout.setContentsMargins(0, 0, 0, 0)
        # hlayout.setSpacing(0)

        # buttonslayout = QVBoxLayout()

        self.labels = []

        self.menuButton = QPushButton(u"\U00002261")
        self.menuLabel = QLabel("Menu")
        myFontBold = self.menuLabel.font()
        myFontBold.setBold(True)
        # buttons
        myFont = self.menuButton.font()
        myFont2 = self.menuButton.font()
        if (myFont.pointSize() > 0):
            myFont.setPointSizeF(1.25 * myFont.pointSizeF())
            myFont2.setPointSizeF(1.4 * myFont.pointSizeF())
        else:
            myFont.setPixelSize(1.25 * myFont.pixelSize())
            myFont2.setPixelSize(1.4 * myFont.pixelSize())
        self.menuLabel.setFont(myFontBold)
        width = self.menuButton.fontMetrics().boundingRect("OO").width() + 7
        height = width  # okButton.height()
        self.menuButton.setFont(myFont2)
        self.menuButton.setMaximumWidth(width)
        self.menuButton.setMinimumWidth(width)
        self.menuButton.setFlat(True)
        self.menuButton.clicked.connect(self.menuPressed)

        mainButton = QPushButton(u"\U0000239A")
        mainLabel = QLabel("Main")
        width = mainButton.fontMetrics().boundingRect("OO").width() + 7
        height = width  # okButton.height()
        mainButton.setFont(myFont2)
        mainButton.setMaximumWidth(width)
        mainButton.setMinimumWidth(width)
        mainButton.clicked.connect(self.main)
        mainButton.setFlat(True)
        setupButton = QPushButton(u"\U0001F527")
        setupLabel = QLabel("Setup")
        setupButton.setFont(myFont)
        setupButton.setFlat(True)
        setupButton.setMaximumWidth(width)
        setupButton.setMinimumWidth(width)
        setupButton.clicked.connect(self.setup)

        identifyButton = QPushButton(u"\U00002755")
        identifyLabel = QLabel("Identify")
        identifyButton.setFont(myFont)
        identifyButton.setFlat(True)
        identifyButton.setMaximumWidth(width)
        identifyButton.setMinimumWidth(width)
        identifyButton.clicked.connect(self.identify)

        self.refreshButton = QPushButton(u"\U000021BB")
        self.refreshLabel = QLabel("Detect")
        self.refreshButton.setFont(myFont)
        self.refreshButton.setFlat(True)
        self.refreshButton.setMaximumWidth(width)
        self.refreshButton.setMinimumWidth(width)
        self.refreshButton.clicked.connect(self.refreshPressed)

        aboutButton = QPushButton(u"\U00002754")
        aboutLabel = QLabel("About")
        aboutButton.setFont(myFont)
        aboutButton.setFlat(True)
        aboutButton.setMaximumWidth(width)
        aboutButton.setMinimumWidth(width)
        aboutButton.clicked.connect(self.about)

        # closeButton = QPushButton(u"\U00002573")
        closeButton = QPushButton(u"\U000026CC")
        closeLabel = QLabel("Close")
        closeButton.setFont(myFont)
        closeButton.setFlat(True)
        closeButton.setMaximumWidth(width)
        closeButton.setMinimumWidth(width)
        closeButton.clicked.connect(self.close_)

        buttongrid = QGridLayout()
        buttongrid.addWidget(self.menuButton, 0, 0)
        buttongrid.addWidget(mainButton, 1, 0)
        buttongrid.addWidget(setupButton, 2, 0)
        buttongrid.addWidget(self.refreshButton, 3, 0)
        buttongrid.addWidget(identifyButton, 4, 0)
        buttongrid.addWidget(aboutButton, 6, 0)
        buttongrid.addWidget(closeButton, 7, 0)

        buttongrid.addWidget(self.menuLabel, 0, 1)
        buttongrid.addWidget(mainLabel, 1, 1)
        buttongrid.addWidget(setupLabel, 2, 1)
        buttongrid.addWidget(self.refreshLabel, 3, 1)
        buttongrid.addWidget(identifyLabel, 4, 1)
        buttongrid.addWidget(aboutLabel, 6, 1)
        buttongrid.addWidget(closeLabel, 7, 1)
        self.labels.append(self.menuLabel)
        self.labels.append(mainLabel)
        self.labels.append(setupLabel)
        self.labels.append(self.refreshLabel)
        self.labels.append(identifyLabel)
        self.labels.append(aboutLabel)
        self.labels.append(closeLabel)
        self.menuLabel .mousePressEvent = self.menuLabelPressed
        mainLabel .mousePressEvent = self.mainLabel
        setupLabel.mousePressEvent = self.setupLabel
        self.refreshLabel.mousePressEvent = self.refreshLabelPressed
        identifyLabel.mousePressEvent = self.identifyLabel
        aboutLabel.mousePressEvent = self.aboutLabel
        closeLabel.mousePressEvent = self.closeLabel

        buttongrid.setRowStretch(0, 0)
        buttongrid.setRowStretch(1, 0)
        buttongrid.setRowStretch(2, 0)
        buttongrid.setRowStretch(3, 0)
        buttongrid.setRowStretch(4, 0)
        buttongrid.setRowStretch(5, 1)
        buttongrid.setRowStretch(6, 0)
        buttongrid.setRowStretch(7, 0)
        self.labels_set_visible(False)

        self.layout = QHBoxLayout()

        # buttonslayout.addWidget(mainButton)
        # buttonslayout.addWidget(setupButton)
        # buttonslayout.addStretch(1)
        # buttonslayout.addWidget(aboutButton)
        # hlayout.addLayout(buttonslayout)
        # hlayout.addLayout(buttongrid)

        # grid.addLayout(hlayout, 1, 1)
        buttongrid.setSpacing(0)

        self.layout.addLayout(buttongrid)

        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 1)
        self.body_layout.setSpacing(0)

        self.title_layout = QHBoxLayout()
        self.title_layout.setContentsMargins(0, 0, 0, 0)
        self.title_layout.setSpacing(0)
        self.titleLabel = QLabel("Monitor Control")
        self.titleLabel.setWordWrap(True)
        self.titleLabel.setSizeIncrement(10, 10)
        myFont = self.titleLabel.font()
        myFont.setBold(True)
        self.titleLabel.setFont(myFont)
        width = self.titleLabel.fontMetrics().boundingRect("OO").width() + 7
        height = width  # okButton.height()
        self.titleLabel.mousePressEvent = self.mainLabel

        self.backButton = QPushButton(u"\U00002190", self)
        myFont = self.backButton.font()
        myFont.setBold(True)
        self.backButton.setFont(myFont)
        self.backButton.setMaximumWidth(width)
        self.backButton.setMinimumWidth(width)
        self.backButton.setFlat(True)
        self.backButton.clicked.connect(self.main)
        self.titleLabel.setMinimumHeight(self.backButton.height())

        self.title_layout.addWidget(self.backButton, 0, QtCore.Qt.AlignVCenter)
        self.title_layout.addSpacing(20)
        self.title_layout.addWidget(self.titleLabel, 1, QtCore.Qt.AlignVCenter)
        # self.backButton.setAlignment(Qt.AlignTop)
        self.title_layout.setAlignment(QtCore.Qt.AlignTop)

        self.body_layout.addLayout(self.title_layout)

        self.main_frame = QtWidgets.QFrame(self)
        self.main_layout = QVBoxLayout()
        self.feature_brightness = FeatureWidget(
            self.main_frame, "Brightness", self.app.brightness)
        self.feature_contrast = FeatureWidget(
            self.main_frame, "Contrast", self.app.contrast)
        self.main_layout.addWidget(self.feature_brightness)
        self.main_layout.addWidget(self.feature_contrast)
        self.main_layout.addStretch(1)
        self.main_frame.setLayout(self.main_layout)
        self.main_frame.hide()
        self.body_layout.addWidget(self.main_frame, 1)

        self.setup_frame = QtWidgets.QFrame(self)

        leftButton = QPushButton("<", self.setup_frame)
        width = leftButton.fontMetrics().boundingRect("<").width() + 7
        leftButton.setFlat(True)
        leftButton.setMaximumWidth(width)
        leftButton.setMinimumWidth(width)
        leftButton.setSizePolicy(QtWidgets.QSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Expanding))

        self.setup_layout = QHBoxLayout()
        self.setup_layout.addWidget(leftButton)
        self.feature_setup_widget = FeatureSetupWidget(
            self.app, self.setup_frame)
        # hlayout.addWidget(self.feature_setup_widget, 1)
        self.feature_setup_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        rightButton = QPushButton(">", self.setup_frame)
        rightButton.setFlat(True)
        rightButton.setMaximumWidth(width)
        rightButton.setMinimumWidth(width)
        rightButton.setSizePolicy(QtWidgets.QSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Expanding))
        self.setup_layout.addWidget(self.feature_setup_widget, 1)
        self.setup_layout.addWidget(rightButton)
        self.setup_layout.setContentsMargins(0, 0, 0, 0)
        self.setup_layout.setSpacing(0)
        leftButton.clicked.connect(self.feature_setup_widget.previous)
        rightButton.clicked.connect(self.feature_setup_widget.next)

        self.setup_frame.setLayout(self.setup_layout)

        # self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)
        self.body_layout.addWidget(self.setup_frame, 1)

        self.layout.addLayout(self.body_layout, 1)

        self.about_frame = QtWidgets.QFrame(self)
        self.about_layout = QVBoxLayout()
        self.aboutLabel1 = QLabel("About", self.about_frame)
        self.aboutLabel1.setWordWrap(True)
        myFont = self.aboutLabel1.font()
        myFont.setBold(True)
        self.aboutLabel1.setFont(myFont)
        about = "©️ ™️ Juno\n\nMonitor Control synchronizes your monitor hardware properties like brightness and contrast.\nThese properties can be changed by the software sliders, or monitor buttons. These changes are monitored and read, and subsequently set to the other monitors using a calibration. This will ensure an input change has the same result on all monitors.\n"
        self.aboutLabel2 = QLabel("{}".format(about), self.about_frame)
        self.aboutLabel2.setAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.aboutLabel2.setWordWrap(True)
        self.about_layout.addWidget(self.aboutLabel1)
        self.about_layout.addWidget(self.aboutLabel2, 1)
        self.about_frame.setLayout(self.about_layout)
        self.about_frame.hide()
        self.body_layout.addWidget(self.about_frame, 1)

        # self.layout.setSizeConstraint(QtGui.QLayout.setFixedSize)

        self.setLayout(self.layout)

        self.setWindowIcon(QtGui.QIcon('artifacts/icon.png'))
        # set the title
        self.setWindowTitle("Monitors Control")

        self.main()

        self.setFixedSize(400, 150)

    def labels_set_visible(self, visible):
        for label in self.labels:
            if (self.refreshLabel == label) and visible:
                self.refreshLabel.setVisible(self.refreshButton.isVisible())
            else:
                label.setVisible(visible)

    def refresh_visible(self, visible):
        if (visible):
            self.refreshButton.setVisible(visible)
            self.refreshLabel.setVisible(self.menuLabel.isVisible())
        else:
            self.refreshLabel.setVisible(visible)
            self.refreshButton.setVisible(visible)

    def focusOutEvent(self, event):
        print('Lost focus')

    def menuLabelPressed(self, event):
        self.menuPressed()

    def menuPressed(self):
        print("Menu")
        self.labels_set_visible(not self.labels[0].isVisible())

    def aboutLabel(self, event):
        self.about()

    def about(self):
        print("About")
        self.setupUpdate()

        self.setMinimumSize(200, 130)

        # self.feature_setup_widget.hide()
        self.setup_frame.hide()
        self.main_frame.hide()
        self.refresh_visible(False)
        self.backButton.show()
        self.about_frame.show()

        self.move(self.window_position)
        self.setFixedSize(self.window_size)

    def closeLabel(self, event):
        self.close_()

    def close_(self):
        print("Close {}".format(len(self.app.identifyWindows)))
        self.setupUpdate()
        if (len(self.app.identifyWindows) == 0):
            self.hide()

    def setupLabel(self, event):
        self.setup()

    def setup(self):
        print("Setup")
        self.move(self.window_position + self.window_position_offset)
        self.setFixedSize(self.window_size + self.window_size_offset)

        self.app.monitors._calibrations.loadYaml()

        self.feature_setup_widget.init()
        self.backButton.show()

        self.main_frame.hide()
        self.about_frame.hide()
        self.refresh_visible(True)
        self.setup_frame.show()

        self.setMinimumSize(200, 130)

    def setupUpdate(self):
        if (self.setup_frame.isVisible()):
            self.app.monitors._calibrations.saveYaml()

    def mainLabel(self, event):
        self.main()

    def main(self):
        print("Main")

        self.setMinimumSize(200, 130)
        self.setupUpdate()

        self.refresh_visible(False)
        self.backButton.hide()
        # self.feature_setup_widget.hide()
        self.setup_frame.hide()
        self.about_frame.hide()
        self.main_frame.hide()

        self.move(self.window_position)
        self.setFixedSize(self.window_size)

        self.main_frame.show()

    def identifyLabel(self, event):
        self.identify()

    def identify(self):
        print("Identify")

        self.app.identify()

    def refreshLabelPressed(self, event):
        self.refreshPressed()

    def refreshPressed(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        print("detect")
        self.feature_setup_widget.clear()
        self.app.detect()
        self.setup()
        self.feature_setup_widget.set_infos(self.app.monitors)
        self.feature_setup_widget.init()

        self.app.list_monitors()

        QApplication.restoreOverrideCursor()

    def position_show(self):
        print("position_show")
        self.app.position_next_to_tray()
        self.main()
        self.show()
        # self.requestActivate()
        # QtCore.Qt.ActiveWindowFocusReason
        self.activateWindow()
        self.setFocus(QtCore.Qt.PopupFocusReason)

    def contrast(self, value):
        # from gui
        self.app.contrast(value)

    def brightness(self, value):
        # from gui
        self.app.brightness(value)

    def set_contrast(self, value):
        # to gui
        self.feature_contrast.set_value(value)
        self.feature_setup_widget.set_contrast(value)

    def set_brightness(self, value):
        # to gui
        self.feature_brightness.set_value(value)
        self.feature_setup_widget.set_brightness(value)

    def show(self):
        # to gui
        value = self.app.monitors.get_contrast()
        if (value is not None):
            self.set_contrast(value)

        value = self.app.monitors.get_brightness()
        if (value is not None):
            self.set_brightness(value)

        self.feature_setup_widget.set_infos(self.app.monitors)

        super().show()


class FeatureSetup():
    def __init__(self, name):
        self.name = name
        self.next = ""
        self.previous = ""


class FeaturesSetup():
    def __init__(self):
        self.features = []
        self.features.append(FeatureSetup("Information"))
        self.features.append(FeatureSetup("Brightness"))
        self.features.append(FeatureSetup("Contrast"))
        self.set_names()

    def set_names(self):
        i = 0
        while (len(self.features) > i):
            p = i - 1
            n = i + 1

            if (len(self.features) <= n):
                n = 0

            if (p < 0):
                p = len(self.features) - 1

            print('{} {} {}'.format(i, p, n))
            self.features[p].previous = self.features[i].name
            self.features[n].next = self.features[i].name

            i += 1

    def get(self, feature):
        i = 0
        while (len(self.features) > i):
            if (self.features[i].name == feature):
                return features[i]
        return None

    def get_next(self, feature):
        if (feature is None):
            return self.features[0]
        i = 0
        while (self.features[i] != feature):
            i += 1

        i += 1
        if (len(self.features) <= i):
            i = 0
        return self.features[i]

    def get_previous(self, feature):
        if (feature is None):
            return self.features[0]
        i = 0
        while (self.features[i] != feature):
            i += 1

        i -= 1
        if (0 > i) or (len(self.features) <= i):
            i = (len(self.features) - 1)
        return self.features[i]


def tab_name(index, infos):
    name = ''
    seperator = ''
    if "Name" in infos.keys():
        name = infos["Name"]
        seperator = ': '
    elif "Manufacturer" in infos.keys():
        name = infos["Manufacturer"]
        seperator = ': '

    return "{}{}{}".format(index+1, seperator, name)


class FeatureSetupWidget(QWidget):

    def __init__(self, app, parent):
        super().__init__(parent)

        self.app = app
        self.parent = parent
        self.features = FeaturesSetup()

        self.layout = QVBoxLayout()

        self.title = QLabel("Brightness", self)
        myFont = self.title.font()
        myFont.setBold(True)
        self.title.setFont(myFont)
        self.title.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.title.setAlignment(QtCore.Qt.AlignCenter)

        self.leftButton = QPushButton(u"\U00002190 Info", self)
        self.leftButton.setFlat(True)
        self.leftButton.setStyleSheet("QPushButton { text-align: left; }")
        self.leftButton.clicked.connect(self.previous)
        self.title_layout = QHBoxLayout()
        self.title_layout.addWidget(self.leftButton, 1)
        self.rightButton = QPushButton(u"Contrast \U00002192", self)
        self.rightButton.setFlat(True)
        self.rightButton.setStyleSheet("QPushButton { text-align: right; }")
        self.rightButton.clicked.connect(self.next)
        self.title_layout.addWidget(
            self.title, 1, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)
        self.title_layout.addWidget(self.rightButton, 1)
        self.title_layout.setContentsMargins(0, 0, 0, 0)
        self.title_layout.setSpacing(0)

        self.info_frame = QtWidgets.QFrame(self)
        self.info_layout = QVBoxLayout()
        self.info_layout.setContentsMargins(0, 0, 0, 0)
        self.info_layout.setSpacing(0)
        self.info_frame.setLayout(self.info_layout)

        # Initialize tab screen
        self.infos = QTabWidget(self.info_frame)
        self.info_layout.addWidget(self.infos, 1)

        self.setup_frame = QtWidgets.QFrame(self)
        self.setup_layout = QVBoxLayout()
        self.setup_layout.setContentsMargins(0, 0, 0, 0)
        self.setup_layout.setSpacing(0)
        self.setup_frame.setLayout(self.setup_layout)

        self.slider = QSlider(QtCore.Qt.Horizontal, self)

        slider_color = Application.Application.getAccentColor()
        self.slider.setStyleSheet(
            "QSlider::handle:horizontal {background-color: " + slider_color.name() + ";}")

        self.slider.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.slider.setRange(0, 100)
        self.slider.setTickInterval(10)
        self.slider.setPageStep(10)
        self.slider.setSingleStep(1)
        self.slider.valueChanged.connect(self.value_change)

        self.calibration = QLabel('{}:'.format("  Calibration"), self)
        self.title.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        # Initialize tab screen
        self.calibrations = QTabWidget(self.setup_frame)
        self.calibration1 = QWidget(self.calibrations)
        self.calibration2 = QWidget(self.calibrations)

        # Add calibrations
        self.calibrations.addTab(self.calibration1, "1: CMN")
        self.calibrations.addTab(self.calibration2, "2: HPN")

        # Create first tab
        self.calibration1.layout = QVBoxLayout()
        self.pushButton1 = QPushButton("PySide2 button", self)
        self.calibration1.layout.addWidget(self.pushButton1)
        self.calibration1.setLayout(self.calibration1.layout)

        # Add calibrations to widget
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addLayout(self.title_layout)
        self.layout.addWidget(self.info_frame, 1)
        self.layout.addWidget(self.setup_frame, 1)

        self.setup_layout.addWidget(self.slider)
        self.setup_layout.addWidget(self.calibration)
        self.setup_layout.addWidget(self.calibrations)

        self.info_frame.hide()

        self.setLayout(self.layout)

        self.init()

    def init(self):
        self.feature = self.features.get_next(None)
        self.set_feature(self.feature)

    def clear(self):
        while(self.infos.count() > 0):
            self.infos.removeTab(0)

    def value_change(self):
        value = self.slider.value()
        print('FeatureSetupWidget {} value change {}'.format(
            self.feature.name, value))
        if (self.feature.name == "Contrast"):
            self.app.contrast(value)
        if (self.feature.name == "Brightness"):
            self.app.brightness(value)

    def set_contrast(self, value):
        # to gui
        if (self.feature.name == "Contrast"):
            self.slider.blockSignals(True)
            self.slider.setValue(value)
            self.slider.blockSignals(False)

    def set_brightness(self, value):
        # to gui
        if (self.feature.name == "Brightness"):
            self.slider.blockSignals(True)
            self.slider.setValue(value)
            self.slider.blockSignals(False)

    def set_feature(self, feature_setup):
        self.info_frame.setVisible(
            self.features.get_next(None) == feature_setup)
        self.setup_frame.setVisible(
            self.features.get_next(None) != feature_setup)

        self.title.setText(feature_setup.name)
        self.leftButton.setText(u"\U00002190 {}".format(feature_setup.next))
        self.rightButton.setText(
            u"{} \U00002192".format(feature_setup.previous))

        value = None
        if (self.feature.name == "Contrast"):
            self.set_contrast_tabs()
            value = self.app.monitors.get_contrast()
        if (self.feature.name == "Brightness"):
            self.set_brightness_tabs()
            value = self.app.monitors.get_brightness()
        print('FeatureSetupWidget {} value set {}'.format(
            self.feature.name, value))
        if (value is not None):
            self.slider.blockSignals(True)
            self.slider.setValue(value)
            self.slider.blockSignals(False)

    def next(self):
        self.feature = self.features.get_next(self.feature)
        self.set_feature(self.feature)

    def previous(self):
        self.feature = self.features.get_previous(self.feature)
        self.set_feature(self.feature)

    # @ pyqtSlot()
    # def on_click(self):
    #    print("\n")
    #    for currentQTableWidgetItem in self.tableWidget.selectedItems():
    #        print(currentQTableWidgetItem.row(),
    #              currentQTableWidgetItem.column(), currentQTableWidgetItem.text())

    def set_infos(self, monitors):
        self.monitors = monitors

        while(self.infos.count() > 0):
            self.infos.removeTab(0)

        index = 0
        monitor = self.monitors.get_monitor(index)
        while (monitor is not None):

            info_widget = QWidget(self.infos)

            info_layout = QVBoxLayout()
            info_grid = QGridLayout()
            info_grid.setColumnStretch(0, 1)
            info_grid.setColumnStretch(1, 3)
            row = 0
            for key, value in monitor._monitor.info.items():
                variableLabel = QLabel(key)
                valueLabel = QLabel(value)

                info_grid.addWidget(variableLabel, row, 0)
                info_grid.addWidget(valueLabel, row, 1)

                row += 1

            info_layout.addLayout(info_grid)
            info_layout.addStretch(1)

            info_widget.setLayout(info_layout)

            self.infos.addTab(
                info_widget, tab_name(index, monitor._monitor.info))

            index += 1
            monitor = self.monitors.get_monitor(index)

    def update_cal_data(self, datas, values):
        print("-> update_cal_data {} : {}".format(datas, values))
        id = datas[0]
        monitor = self.monitors.get_monitor_by_id(id)
        type = datas[1]
        x_values = values[0]
        y_values = values[1]

        calibration = monitor._calibration.get(type)
        if (calibration is not None):
            calibration._set(values)

    def set_brightness_tabs(self):
        while(self.calibrations.count() > 0):
            self.calibrations.removeTab(0)

        index = 0
        monitor = self.monitors.get_monitor(index)
        while (monitor is not None):
            if (monitor._monitor.brightness is not None):

                type = Display.Display.BRIGHTNESS
                calibration_scaler = monitor._calibration.get(type)
                if (calibration_scaler is not None):

                    back_color = self.calibrations.palette().color(QtGui.QPalette.Base).name()
                    text_color = self.calibrations.palette().color(QtGui.QPalette.WindowText).name()
                    line_color = Application.Application.getAccentColor()

                    calibration_widget = CalibrationWidget.CalibrationWidget(self,
                                                                             calibration_scaler._scaling, self.update_cal_data,
                                                                             [monitor._monitor._device_name, type],
                                                                             back_color, text_color, line_color)

                    self.calibrations.addTab(
                        calibration_widget, tab_name(index, monitor._monitor.info))

            index += 1
            monitor = self.monitors.get_monitor(index)

    def set_contrast_tabs(self):
        while(self.calibrations.count() > 0):
            self.calibrations.removeTab(0)

        index = 0
        monitor = self.monitors.get_monitor(index)
        while (monitor is not None):
            if (monitor._monitor.contrast is not None):

                type = Display.Display.CONTRAST
                calibration_scaler = monitor._calibration.get(type)

                if (calibration_scaler is not None):

                    back_color = self.calibrations.palette().color(QtGui.QPalette.Base).name()
                    text_color = self.calibrations.palette().color(QtGui.QPalette.WindowText).name()
                    line_color = Application.Application.getAccentColor()

                    calibration_widget = CalibrationWidget.CalibrationWidget(self,
                                                                             calibration_scaler._scaling, self.update_cal_data,
                                                                             [monitor._monitor._device_name, type],
                                                                             back_color, text_color, line_color)

                    self.calibrations.addTab(
                        calibration_widget, tab_name(index, monitor._monitor.info))

            index += 1
            monitor = self.monitors.get_monitor(index)


class FeatureWidget(QWidget):

    def __init__(self, parent, name, valuechange):
        super().__init__(parent)

        self.valuechange = valuechange

        self.layout = QVBoxLayout()
        self.name = name
        self.title = QLabel('{}:'.format(name), self)
        self.title.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        self.slider = QSlider(QtCore.Qt.Horizontal, self)

        slider_color = Application.Application.getAccentColor()
        self.slider.setStyleSheet(
            "QSlider::handle:horizontal {background-color: " + slider_color.name() + ";}")

        self.slider.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.slider.setRange(0, 100)
        self.slider.setTickInterval(10)
        self.slider.setPageStep(10)
        self.slider.setSingleStep(1)
        self.slider.valueChanged.connect(self.value_change)

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.slider)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.setLayout(self.layout)

    def value_change(self):
        value = self.slider.value()
        print('FeatureWidget {} value change {}'.format(self.name, value))
        self.valuechange(value)

    def set_value(self, value):
        print('FeatureWidget {} 1 set value {}'.format(self.name, value))
        self.slider.blockSignals(True)
        self.slider.setValue(value)
        self.slider.blockSignals(False)
        print('FeatureWidget {} 2 set value {}'.format(self.name, value))


RUN_PATH = "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
THEME_PATH = "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize"
ACCENT_PATH = r'HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Accent'


if __name__ == '__main__':
    # print(os.environ['QT_API'])

    getAccentColor()

    app = Application(sys.argv)

    # settings = QSettings(RUN_PATH, QSettings.NativeFormat)

    # clock = Window()

    # setup stylesheet
    # the default system in qdarkstyle uses qtpy environment variable
    # app.setStyleSheet(qdarkstyle.load_stylesheet())

    # clock.show()
    app.window.position_show()

    sys.exit(app.exec_())
