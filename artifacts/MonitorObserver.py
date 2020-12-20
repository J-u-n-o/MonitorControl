

import struct
import wmi
import threading
import signal
import sys
import MonitorDetect
import ctypes
import ctypes.wintypes as wintypes
import win32api

import traceback
import wmi
import os
import pythoncom
import Scaler
import Display
import Config


class Monitors:
    def __init__(self):
        self._monitor_observers = []

        self._calibrations = Config.Calibrations()
        self._calibrations.loadYaml()

    def set_brightness(self, brightness, monitor_observer=None):
        print('  all brightness {}'.format(brightness))
        for _monitor_observer in self._monitor_observers:
            if (monitor_observer != _monitor_observer):
                _monitor_observer.set_brightness(brightness)

    def set_contrast(self, contrast, monitor_observer=None):
        print('  all contrast {}'.format(contrast))
        for _monitor_observer in self._monitor_observers:
            if (monitor_observer != _monitor_observer):
                _monitor_observer.set_contrast(contrast)

    def get_contrast(self):
        contrast = None
        for _monitor_observer in self._monitor_observers:
            if (type(_monitor_observer) == MonitorObserver):
                contrast = _monitor_observer.get_contrast()
                if (contrast is not None):
                    return contrast
        return None

    def get_brightness(self):
        brightness = None
        for _monitor_observer in self._monitor_observers:
            if (type(_monitor_observer) == MonitorObserver):
                brightness = _monitor_observer.get_brightness()
                if (brightness is not None):
                    return brightness
        return None

    def remove_displays(self):

        i = 0
        while (len(self._monitor_observers) > 0) and (i < len(self._monitor_observers)):
            _monitor_observer = self._monitor_observers[i]
            if (type(_monitor_observer) == MonitorObserver):
                self._monitor_observers.remove(_monitor_observer)
            else:
                i += 1

    def detect_monitors(self):
        self.remove_displays()

        displays = MonitorDetect.get_displays()
        for display in displays:
            self.add_display(display)

            print("Display Type {}".format(type(display)))
            print(" brightness {}".format(display.brightness))
            print(" wmi {}".format(display.wmi))

            model = display.capabilities['model']
            print(" model {}".format(model))

    def add_display(self, display):
        calibration = self._calibrations.get(display._device_name)

        if (display.contrast is not None):
            calibration.ensure(Display.Display.CONTRAST)

        if (display.brightness is not None):
            calibration.ensure(Display.Display.BRIGHTNESS)

        self.add_observer(
            MonitorObserver(self, display, calibration))

    def add_observer(self, observer):
        self._monitor_observers.append(observer)

    def tick(self):
        for _monitor_observer in self._monitor_observers:
            if (type(_monitor_observer) == MonitorObserver):
                _monitor_observer.tick()

    def get_monitor(self, index):
        i = 0
        for _monitor_observer in self._monitor_observers:
            if (type(_monitor_observer) == MonitorObserver):
                if (i == index):
                    return _monitor_observer
                i += 1
        return None

    def get_monitor_by_id(self, id):
        for _monitor_observer in self._monitor_observers:
            if (type(_monitor_observer) == MonitorObserver):
                if (id == _monitor_observer._monitor._device_name):
                    return _monitor_observer
        return None


class MonitorObserver:
    def __init__(self, monitor_observers, monitor, calibration):
        self._monitor_observers = monitor_observers
        self._monitor = monitor
        self._calibration = calibration

        self._brightness = self._monitor.brightness
        self._scaled_brightness = -1

        self._contrast = self._monitor.contrast
        self._scaled_contrast = -1

    def tick(self):
        brightness = self._monitor.brightness
        # print(' tick {} brightness {} =?= {}'.format(
        #    self._monitor._id, brightness, self._brightness))
        if (brightness != self._brightness):
            new_brightness = self._calibration.get(Display.Display.BRIGHTNESS)._get_inv(
                brightness)
            print('  update brightness {}'.format(brightness, new_brightness))
            self._monitor_observers.set_brightness(new_brightness, self)
            self._brightness = new_brightness

        contrast = self._monitor.contrast
        # print(' tick {} contrast {} =?= {}'.format(
        #    self._monitor._id, contrast, self._contrast))
        if (contrast != self._contrast):
            new_contrast = self._calibration.get(Display.Display.CONTRAST)._get_inv(
                contrast)
            print('  update contrast {}'.format(contrast, new_contrast))
            self._monitor_observers.set_contrast(new_contrast, self)
            self._contrast = new_contrast

    def set_brightness(self, brightness):
        if (self._calibration.get(Display.Display.BRIGHTNESS) is None):
            print('  no brightness {}'.format(self._monitor._id))
            return

        scaled_brightness = self._calibration.get(Display.Display.BRIGHTNESS)._get(
            brightness)
        print(' set_brightness  {}  {} -> {} =?= {}'.format(self._monitor._id, brightness, scaled_brightness,
                                                            self._scaled_brightness))
        if (scaled_brightness != self._scaled_brightness):
            if (scaled_brightness != self._monitor.brightness):
                print('     {} -> {} -> {}'.format(self._brightness,
                                                   self._monitor.brightness, scaled_brightness))
                self._monitor.brightness = scaled_brightness
            self._brightness = self._monitor.brightness
            self._scaled_brightness = scaled_brightness

    def set_contrast(self, contrast):
        if (self._calibration.get(Display.Display.CONTRAST) is None):
            print('  no contrast {}'.format(self._monitor._id))
            return

        scaled_contrast = self._calibration.get(Display.Display.CONTRAST)._get(
            contrast)
        print('  set_contrast {}  {} -> {} =?= {}'.format(self._monitor._id, contrast, scaled_contrast,
                                                          self._scaled_contrast))
        if (scaled_contrast != self._scaled_contrast):
            if (scaled_contrast != self._monitor.contrast):
                print('     {} -> {} -> {}'.format(self._contrast,
                                                   self._monitor.contrast, scaled_contrast))
                self._monitor.contrast = int(scaled_contrast)
            self._contrast = self._monitor.contrast
            self._scaled_contrast = scaled_contrast

    def get_contrast(self):
        contrast = None
        contrast = self._monitor.contrast
        if (contrast is None):
            return None
        return self._calibration.get(Display.Display.CONTRAST)._get_inv(contrast)

    def get_brightness(self):
        brightness = None
        brightness = self._monitor.brightness
        if (brightness is None):
            return None
        return self._calibration.get(Display.Display.BRIGHTNESS)._get_inv(brightness)

# https://stackoverflow.com/questions/59914907/how-can-i-detect-brightness-changes-using-python-and-wmi-on-windows-10


observe_timer = None
application_running = True
displays = []
monitors = None


def observe():
    global observe_timer
    global monitors
    observe_timer = threading.Timer(1.0, observe)
    observe_timer.start()
    # print("monitors.tick()")
    pythoncom.CoInitialize()
    monitors.tick()


def signal_handler(sig, frame):
    global application_running
    print('You pressed Ctrl+C!')
    application_running = False
    observe_timer.cancel()
    sys.exit(0)
# pip install wmi


if __name__ == '__main__':
    print('Display.BRIGHTNESS {}'.format(Display.Display.BRIGHTNESS))

    print(8 * struct.calcsize("P"))

    monitors = Monitors()

    displays = MonitorDetect.get_displays()
    for display in displays:
        monitors.add_display(display)

        print("Display Type {}".format(type(display)))
        print(" brightness {}".format(display.brightness))
        print(" wmi {}".format(display.wmi))

        model = display.capabilities['model']
        print(" model {}".format(model))

    observe()

    c = wmi.WMI(namespace='wmi')
    brightness_watcher = c.WmiMonitorBrightnessEvent.watch_for(notification_type="Modification"
                                                               # delay_secs=1
                                                               )

    signal.signal(signal.SIGINT, signal_handler)

    while (application_running):
        try:
            event_happened = brightness_watcher(timeout_ms=10)
        except wmi.x_wmi_timed_out:
            event_happened = None
            # handle_com_error()
        if (event_happened is not None):
            print(event_happened)
