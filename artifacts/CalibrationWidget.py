

# First include PySide2 before maplotlib!!!
# Otherwise 'wrong argument type' errors related to QWidget
# To prevent autopep8 formater to move PySide2 down add '# noqa: E402'
from PySide2.QtWidgets import QVBoxLayout  # noqa: E402
#from PyQt5 import QtCore, QtWidgets  # noqa: E402
from PySide2 import QtCore, QtWidgets, QtGui  # noqa: E402
from PySide2.QtWidgets import QTabWidget, QGroupBox, QPushButton  # noqa: E402

import matplotlib
matplotlib.use('Qt5Agg')  # noqa: E402

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


from matplotlib.backend_bases import MouseEvent
import Application
import os
import sys  # We need sys so that we can pass argv to QApplication
import math

# https://stackoverflow.com/questions/28001655/draggable-line-with-draggable-points

# https://stackoverflow.com/questions/58075822/pyside2-and-matplotlib-how-to-make-matplotlib-run-in-a-separate-process-as-i


import sys
import matplotlib

os.environ["QT_API"] = "PySide2"
matplotlib.use('Qt5Agg')
# print('matplotlib.rcParams: {}'.format(matplotlib.rcParams.keys()))
# matplotlib.rcParams['backend.qt5'] = 'PySide2'

# Some application specific functions:


def IntSeries(data_series):
    l = len(data_series)
    i = 0
    while i < l:
        data_series[i] = int(data_series[i])
        i += 1
    return data_series


def fix_series(data_series):
    # All should be integer
    IntSeries(data_series)

    # And:
    # - Increasing or equal
    # - Between 0 and 100
    l = len(data_series)
    i = 1
    while i < len(data_series):
        if data_series[i] < 0:
            data_series[i] = 0
        elif data_series[i] > 100:
            data_series[i] = 100
        elif data_series[i] < data_series[i-1]:
            data_series[i] = data_series[i-1]
        i += 1
    return data_series


def fix_series_end(data_series):
    fix_series(data_series)
    # And also first should be 0, and last 100
    l = len(data_series)
    if (l > 0):
        data_series[0] = 0
    if (l > 1):
        data_series[l-1] = 100
    return data_series


def fix_x_y(x, y):
    l = min(len(x), len(y))
    # print("fix_x_y {} -> {}, {}".format(l, x,
    #                                  y))
    x = x[:l]
    y = y[:l]

    # At least two points at 0, y0 and 100, y100:
    if l == 0:
        x.append(0)
        y.append(0)
        x.append(100)
        y.append(100)
        # print("  0 fix_x_y {} -> {}, {}".format(l, x,
        #                                      y))
    elif l == 1:
        x.append(100)
        y.append(100)
        # print("  1 fix_x_y {} -> {}, {}".format(l, x,
        #                                      y))

    x = fix_series_end(x)
    y = fix_series(y)

    return x, y


def fix_and_clean_x_y(x, y):
    x, y = fix_x_y(x, y)

    i = 1
    d = 0.01
    while i < len(x):
        if (abs(x[i] - x[i-1]) < d) and (abs(y[i] - y[i-1]) < d):
            x.pop(i)
            y.pop(i)
        else:
            i += 1

    return x, y


def add_x_y(x, y, xpoint, ypoint):
    index = None
    x, y = fix_and_clean_x_y(x, y)

    xpoint = int(xpoint)
    ypoint = int(ypoint)

    if (xpoint > 0) and (xpoint < 100) and (ypoint > 0) and (ypoint < 100):
        # print("add_x_y {}, {} -> {}, {}".format(xpoint, ypoint, x,
        #                                      y))
        l = len(x)
        i = 1
        while i < len(x):
            if (x[i] > xpoint):
                x.insert(i, xpoint)
                ypoint = min(ypoint, y[i])
                ypoint = max(ypoint, y[i-1])
                y.insert(i, ypoint)
                x, y = fix_x_y(x, y)
                index = i
                break
            else:
                i += 1

    return x, y, index


def remove_x_y(x, y, xpoint, ypoint):
    index = None
    x, y = fix_and_clean_x_y(x, y)

    l = len(x)
    i = 0
    while i < len(x):
        if (x[i] == xpoint):
            x.pop(i)
            y.pop(i)
            index = i
            break
        else:
            i += 1

    return x, y, index


def to_x_y_points(data_seriesX, data_seriesY):
    points = []
    l = min(len(data_seriesX), len(data_seriesY))
    i = 0
    while i < l:
        points.append([data_seriesX[i], data_seriesY[i]])
        i += 1
    return points


def to_x_y_arrays(data_series):
    pointsX = []
    pointsY = []
    l = len(data_series)
    i = 0
    while i < l:
        pointsX.append(data_series[i][0])
        pointsY.append(data_series[i][1])
        i += 1
    return pointsX, pointsY

# https://github.com/yuma-m/matplotlib-draggable-plot/blob/master/draggable_plot.py


class CalibrationWidget(FigureCanvas):
    u""" An example of plot with draggable markers """

    def __init__(self, parent, points, callback, callback_data, back_color, text_color, line_color):

        self.textColor = QtGui.QColor(255, 0, 0)
        self.backColor = QtGui.QColor(0, 255, 0)
        self.lineColor = QtGui.QColor(255, 255, 0)

        self.textColor = text_color
        self.backColor = back_color
        self.lineColor = line_color

        self.callback = callback
        self.callback_data = callback_data

        #self.fig = Figure(figsize=(width, height), facecolor='grey')
        #self.fig = Figure(facecolor='grey')
        self.fig = Figure(facecolor=(
            self.backColor.redF(), self.backColor.greenF(), self.backColor.blueF()))
        self.axes = self.fig.add_subplot(1, 1, 1)
        self.fig.tight_layout(pad=2)
        self.fig.subplots_adjust(right=0.99, top=0.99)
        #self.fig.subplots_adjust(right=0.99, left=0.01, bottom=0.01, top=0.99)
        self.axes.set_facecolor(
            (self.backColor.redF(), self.backColor.greenF(), self.backColor.blueF()))
        self.axes.set_xlim(-3, 103)
        self.axes.set_ylim(-5, 105)
        self.axes.grid(which="both", color=(
            self.textColor.redF(), self.textColor.greenF(), self.textColor.blueF()),
            clip_on=False, alpha=1, fillstyle='none')
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['bottom'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.spines['left'].set_visible(False)
        self.axes.xaxis.label.set_color((
            self.textColor.redF(), self.textColor.greenF(), self.textColor.blueF()))
        self.axes.yaxis.label.set_color((
            self.textColor.redF(), self.textColor.greenF(), self.textColor.blueF()))
        for tic in self.axes.xaxis.get_major_ticks():
            tic.tick1line.set_visible(False)
            tic.tick2line.set_visible(False)
        for tic in self.axes.yaxis.get_major_ticks():
            tic.tick1line.set_visible(False)
            tic.tick2line.set_visible(False)

        self.axes.grid(True)

        super().__init__(self.fig)
        self.setParent(parent)

        self.axes.tick_params(axis='both', pad=0.0)
        self.axes.set_xticks([0, 20, 40, 60, 80, 100])
        self.axes.set_yticks([0, 20, 40, 60, 80, 100])
        for item in (self.axes.get_xticklabels() + self.axes.get_yticklabels()):
            item.set_fontsize(7.5)
            item.set_color((
                self.textColor.redF(), self.textColor.greenF(), self.textColor.blueF()))

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self._line = None
        self._dragging_point = None

        self._pointsX, self._pointsY = to_x_y_arrays(points)
        self._pointsX, self._pointsY = fix_and_clean_x_y(
            self._pointsX, self._pointsY)

        self._update_plot()

        self.fig.canvas.mpl_connect('button_press_event', self._on_click)
        self.fig.canvas.mpl_connect(
            'button_release_event', self._on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self._on_motion)

        # plt.show()

    def _update_plot(self):

        # if self._points is not None:
        #    x, y = to_x_y_arrays(self._points)

        self._points = to_x_y_points(self._pointsX, self._pointsY)

        if self._line is None:
            self._line, = self.axes.plot(
                self._pointsX, self._pointsY, color=(self.lineColor.redF(), self.lineColor.greenF(), self.lineColor.blueF()), marker="o", markersize=10)
        else:
            self._line.set_data(self._pointsX, self._pointsY)
        self.fig.canvas.draw()

    def _add_point(self, x, y=None):
        if isinstance(x, MouseEvent):
            x, y = int(x.xdata), int(x.ydata)

        print("_add_point {}, {} -> {}, {}".format(x,
                                                   y, self._pointsX, self._pointsY))

        self._pointsX, self._pointsY, index = add_x_y(
            self._pointsX, self._pointsY, x, y)

        print("_add_point {}: {}, {} -> {}, {}".format(index,
                                                       x, y, self._pointsX, self._pointsY))

        point = [
            self._pointsX[index],
            self._pointsY[index]]

        return index, point

    def _remove_point(self, x, _):

        self._pointsX, self._pointsY, index = remove_x_y(
            self._pointsX, self._pointsY, x)

    def _find_neighbor_point(self, event):
        u""" Find point around mouse position
        :rtype: ((int, int)|None)
        :return: (x, y) if there are any point around mouse else None
        """
        distance_threshold = 3.0
        nearest_point = None
        nearest_point_index = -1
        min_distance = math.sqrt(2 * (100 ** 2))

        i = 0
        for point in self._points:
            x = point[0]
            y = point[1]
            distance = math.hypot(event.xdata - x, event.ydata - y)
            if distance < min_distance:
                min_distance = distance
                nearest_point = (x, y)
                nearest_point_index = i
            i += 1

        if min_distance < distance_threshold:
            print("_find_neighbor_point {}, {} -> {}: {}".format(
                event.xdata, event.ydata, nearest_point, nearest_point_index))
            return nearest_point, nearest_point_index

        print("_find_neighbor_point None")
        return None, -1

    def _on_click(self, event):
        u""" callback method for mouse click event
        :type event: MouseEvent
        """
        # left click
        if event.button == 1 and event.inaxes in [self.axes]:
            point, index = self._find_neighbor_point(event)
            if point:
                self._dragging_point = point
                self._dragging_point_index = index
            else:
                index, point = self._add_point(event)
                self._dragging_point = point
                self._dragging_point_index = index
            self._update_plot()
        # right click
        elif event.button == 3 and event.inaxes in [self.axes]:
            point, index = self._find_neighbor_point(event)
            if point:
                self._points.pop(index)
                self._pointsX, self._pointsY = to_x_y_arrays(self._points)
                self._points = to_x_y_points(self._pointsX, self._pointsY)

            self._update_plot()

    def _on_release(self, event):
        u""" callback method for mouse release event
        :type event: MouseEvent
        """
        print("_on_release {}, {}".format(
            event.xdata, event.ydata))
        # if event.button == 1 and event.inaxes in [self.axes] and self._dragging_point:
        self._dragging_point = None

        self._pointsX, self._pointsY = fix_and_clean_x_y(
            self._pointsX, self._pointsY)

        self._update_plot()

        print("_on_release -> {}".format(
            self._points))

        if (self.callback is not None):
            self.callback(self.callback_data, self._points)

    def _on_motion(self, event):
        u""" callback method for mouse motion event
        :type event: MouseEvent
        """
        # print("_on_motion {}, {}".format(
        #    event.xdata, event.ydata))
        if not self._dragging_point:
            return
        if event.xdata is None or event.ydata is None:
            return

        if (0 == self._dragging_point_index):
            self._pointsX[self._dragging_point_index] = 0
        elif ((len(self._pointsX) - 1) == self._dragging_point_index):
            self._pointsX[self._dragging_point_index] = 100
        else:
            x = event.xdata
            if (x < self._pointsX[self._dragging_point_index-1]):
                x = self._pointsX[self._dragging_point_index-1]
            if (x > self._pointsX[self._dragging_point_index+1]):
                x = self._pointsX[self._dragging_point_index+1]
            x = min(x, 100)
            x = max(x, 0)
            self._pointsX[self._dragging_point_index] = x

        y = event.ydata
        if (0 < self._dragging_point_index):
            if (y < self._pointsY[self._dragging_point_index-1]):
                y = self._pointsY[self._dragging_point_index-1]
        if ((len(self._pointsX) - 1) > self._dragging_point_index):
            if (y > self._pointsY[self._dragging_point_index+1]):
                y = self._pointsY[self._dragging_point_index+1]

        y = min(y, 100)
        y = max(y, 0)
        self._pointsY[self._dragging_point_index] = y

        # self._remove_point(*self._dragging_point)
        # self._dragging_point = self._add_point(event)
        self._update_plot()


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
        self.graphWidget = CalibrationWidget(self.calibrations, [[0, 0], [
                                             100, 100]], self.updated, [1, "test"], back_color, text_color, line_color)
        # self.graphWidget = CalibrationWidget(
        #     self.calibrations, [[0, 0], [100, 100]], self.updated, [1, "test"], back_color, text_color, line_color)

        self.calibrations.addTab(
            self.graphWidget, "graph")

        print('calibrations stylesheet {}'.format(
            self.calibrations.styleSheet()))

        self.setCentralWidget(self.calibrations)


def main():
    # app = Application.Application(sys.argv)
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
