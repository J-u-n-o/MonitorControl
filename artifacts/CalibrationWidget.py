
from PySide2 import QtWidgets, QtWidgets, QtGui, QtCore
from PySide2.QtWidgets import QTabWidget, QGroupBox, QPushButton

from pyqtgraph import PlotWidget, plot
import pyqtgraph
import ctypes
import sys  # We need sys so that we can pass argv to QApplication
import os
import Application


def IntSeries(dataSeries):
    l = len(dataSeries)
    i = 0
    while i < l:
        dataSeries[i] = int(dataSeries[i])
        i += 1
    return dataSeries


def FixSeries(dataSeries):

    IntSeries(dataSeries)

    l = len(dataSeries)
    i = 1
    while i < len(dataSeries):
        if dataSeries[i] < 0:
            dataSeries[i] = 0
        elif dataSeries[i] > 100:
            dataSeries[i] = 100
        elif dataSeries[i] < dataSeries[i-1]:
            dataSeries[i] = dataSeries[i-1]
        i += 1
    return dataSeries


def FixSeriesEnd(dataSeries):
    FixSeries(dataSeries)
    l = len(dataSeries)
    if (l > 0):
        dataSeries[0] = 0
    if (l > 1):
        dataSeries[l-1] = 100
    return dataSeries


def FixXY(x, y):
    l = min(len(x), len(y))
    x = x[:l]
    y = y[:l]
    x = FixSeriesEnd(x)
    y = FixSeries(y)

    return x, y


def FixAndCleanXY(x, y):
    x, y = FixXY(x, y)

    i = 1
    d = 0.01
    while i < len(x):
        if (abs(x[i] - x[i-1]) < d) and (abs(y[i] - y[i-1]) < d):
            x.pop(i)
            y.pop(i)
        else:
            i += 1

    return x, y


def AddXY(x, y, xpoint, ypoint):
    index = None
    x, y = FixAndCleanXY(x, y)

    if (xpoint > 0) and (xpoint < 100) and (ypoint > 0) and (ypoint < 100):
        l = len(x)
        i = 1
        while i < len(x):
            if (x[i] > xpoint):
                x.insert(i, xpoint)
                ypoint = min(ypoint, y[i])
                ypoint = max(ypoint, y[i-1])
                y.insert(i, ypoint)
                x, y = FixXY(x, y)
                index = i
                break
            else:
                i += 1

    return x, y, index


def ToXYPoints(dataSeriesX, dataSeriesY):
    points = []
    l = min(len(dataSeriesX), len(dataSeriesY))
    i = 0
    while i < l:
        points.append([dataSeriesX[i], dataSeriesY[i]])
        i += 1
    return points

# https://stackoverflow.com/questions/23360277/pyqtgraph-custom-plotdataitem-is-not-receiving-mousedragevents


class CalibrationData(pyqtgraph.PlotDataItem):
    def __init__(self, callback, callback_data, pen, symbolBrush):

        self.callback = callback
        self.callback_data = callback_data

        self.dragPoint = None
        self.dragOffset = None
        super().__init__(
            self, pen=pen, symbolBrush=symbolBrush)

        # Need to switch off the "has no contents" flag
        self.setFlags(self.flags() & ~self.ItemHasNoContents)

        index = 0
        spotItem = pyqtgraph.SpotItem(None, self, index)

    def setData(self, x=None, y=None, pen=None, symbolBrush=None):
        if (x is not None) and (y is not None) and (len(x) == len(y)):
            # super().setData(x=datax, y=datay)
            self.datax = x
            self.datay = y
            self.updateGraph()

    def updateGraph(self):
        super().setData(x=self.datax, y=self.datay)
        # super().setData(x=self.datax, y=self.datay)

    def shape(self):
        # Inherit shape from the curve item
        return self.curve.shape()

    def boundingRect(self):
        # All graphics items require this method (unless they have no contents)
        return self.shape().boundingRect()

    def paint(self, p, *args):
        # All graphics items require this method (unless they have no contents)
        return

    def hoverEvent(self, ev):
        # This is recommended to ensure that the item plays nicely with
        # other draggable items
        ev.acceptDrags(QtCore.Qt.LeftButton)

    def mouseDragEvent(self, ev):
        if ev.button() != QtCore.Qt.LeftButton:
            ev.ignore()
            return

        if ev.isStart():
            pos = ev.buttonDownPos()
            pts = self.scatter.pointsAt(pos)
            if len(pts) == 0:
                self.datax, self.datay, index = AddXY(
                    self.datax, self.datay, pos.x(), pos.y())
                if (index is None):
                    ev.ignore()
                    return
                self.dragPoint = pyqtgraph.SpotItem(None, self, index)
                self.updateGraph()
            else:
                self.dragPoint = pts[0]
        elif ev.isFinish():
            self.dragPoint = None
            self.datax, self.datay = FixAndCleanXY(self.datax, self.datay)
            self.updateGraph()
            if (self.callback is not None):
                self.callback(self.callback_data,
                              ToXYPoints(self.datax, self.datay))
            return
        else:
            None

        if self.dragPoint is None:
            ev.ignore()
            return
        pos = ev.pos()

        if (0 == self.dragPoint.index()):
            self.datax[self.dragPoint.index()] = 0
        elif ((len(self.datax) - 1) == self.dragPoint.index()):
            self.datax[self.dragPoint.index()] = 100
        else:
            x = ev.pos().x()
            if (x < self.datax[self.dragPoint.index()-1]):
                x = self.datax[self.dragPoint.index()-1]
            if (x > self.datax[self.dragPoint.index()+1]):
                x = self.datax[self.dragPoint.index()+1]
            x = min(x, 100)
            x = max(x, 0)
            self.datax[self.dragPoint.index()] = x

        y = ev.pos().y()
        if (0 < self.dragPoint.index()):
            if (y < self.datay[self.dragPoint.index()-1]):
                y = self.datay[self.dragPoint.index()-1]
        if ((len(self.datax) - 1) > self.dragPoint.index()):
            if (y > self.datay[self.dragPoint.index()+1]):
                y = self.datay[self.dragPoint.index()+1]

        y = min(y, 100)
        y = max(y, 0)
        self.datay[self.dragPoint.index()] = y

        self.updateGraph()
        ev.accept()


class CalibrationWidget(pyqtgraph.PlotWidget):
    def __init__(self, parent, data_points, callback, callback_data, back_color, text_color, line_color):
        super().__init__(background=back_color)

        self.callback = callback
        self.callback_data = callback_data

        self.back_color = back_color
        self.text_color = text_color
        self.line_color = line_color

        # pyqtgraph.setConfigOption(
        #    'background', pyqtgraph.mkColor(self.backColor))
        pyqtgraph.setConfigOption(
            'foreground', pyqtgraph.mkColor(self.text_color))

        # self.graphWidget =
        # self.setCentralWidget(self.graphWidget)

        x = []
        y = []
        for data in data_points:
            x.append(data[0])
            y.append(data[1])

        x, y = FixXY(x, y)

        # plot data: x, y values
        # self.plot(hour, temperature)

        plotItem = self.getPlotItem()

        brush = pyqtgraph.mkBrush(color=line_color)
        pen = pyqtgraph.mkPen(color=line_color, width=2,
                              style=QtCore.Qt.SolidLine)
        axispen = pyqtgraph.mkPen(color=text_color, width=1,
                                  style=QtCore.Qt.SolidLine)

        self.data = CalibrationData(
            self.callback, self.callback_data, pen, brush)

        plotItem.addItem(self.data)
        # self.data.setData(x=hour, y=temperature)
        self.data.setData(x, y)
        plotItem.showGrid(True, True)
        self.data.setPen(pen)
        self.data.setSymbolPen(pen)
        self.data.setSymbol('o')
        self.data.setSymbolBrush(brush)
        self.data.setBrush(brush)

        plotItem.getAxis('left').setPen(axispen)
        plotItem.getAxis('bottom').setPen(axispen)
        plotItem.getAxis('left').setTextPen(axispen)
        plotItem.getAxis('bottom').setTextPen(axispen)

        plotItem.setContentsMargins(0., 10., 10., 0.)

        self.setXRange(-1, 101, 0)
        self.setYRange(-1, 101, 0)
        self.setLimits(xMin=-1, xMax=100,
                       minXRange=0, maxXRange=100,
                       yMin=-1, yMax=100,
                       minYRange=0, maxYRange=100)
        plotItem.disableAutoRange("xy")

        # self.enableAutoRange(axis='xy')
        plotItem.setAutoVisible(y=False, x=False)
        # self.disableAutoRange(pyqtgraph.ViewBox.YAxis)
        plotItem.setMouseEnabled(False, False)

        # self.plot = pyqtgraph.PlotItem()
        plotItem.setMenuEnabled(False)
        self.hideButtons()
        plotItem.hideButtons()

        self.dragPoint = None
        self.lastIndex = 0
        self.dragOffset = None


class MainWindow(QtWidgets.QMainWindow):

    def updated(self, data, values):
        print("-> {} {}".format(data, values))

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.calibrations = QTabWidget(self)

        palette = self.calibrations.palette()
        back_color = palette.color(self.calibrations.backgroundRole())

        print('groupbox back_color {}'.format(
            back_color.name()))

        # back_color = self.calibrations.backgroundRole()

        # back_color = self.calibrations.backgroundRole())

        if (Application.Application.tabColor is not None):
            back_color = Application.Application.tabColor
        else:
            back_color = self.calibrations.palette().color(QtGui.QPalette.Base)
        text_color = self.calibrations.palette().color(QtGui.QPalette.WindowText)
        line_color = Application.Application.getAccentColor()

        print('groupbox tab_color Base {}'.format(
            self.calibrations.palette().color(QtGui.QPalette.Base).name()))
        print('groupbox tab_color AlternateBase {}'.format(
            self.calibrations.palette().color(QtGui.QPalette.AlternateBase).name()))
        print('groupbox tab_color Midlight {}'.format(
            self.calibrations.palette().color(QtGui.QPalette.Midlight).name()))
        print('groupbox tab_color button {}'.format(
            self.calibrations.palette().color(QtGui.QPalette.Button).name()))
        print('groupbox tab_color {}'.format(
            self.calibrations.palette().color(QtGui.QPalette.Base).name()))
        print('groupbox back_color {}'.format(
            back_color.name()))

        print('groupbox text_color {}'.format(
            text_color.name()))
        print('groupbox line_color {}'.format(
            line_color.name()))

        groupbox = None
        self.graphWidget = CalibrationWidget(
            self.calibrations, [[0, 0], [100, 100]], self.updated, [1, "test"], back_color, text_color, line_color)

        self.calibrations.addTab(
            self.graphWidget, "graph")

        print('calibrations stylesheet {}'.format(
            self.calibrations.styleSheet()))

        self.setCentralWidget(self.calibrations)


def main():
    app = Application.Application(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
