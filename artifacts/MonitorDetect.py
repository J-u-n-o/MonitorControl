

from typing import NamedTuple
import ctypes
import ctypes.wintypes as wintypes
import win32api

import traceback

import Display
import DisplayVcp


# Reference: https://msdn.microsoft.com/en-us/library/dd692982(v=vs.85).aspx

_PHYSICAL_MONITOR_DESCRIPTION_SIZE = 128

_MONITORENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL,
                                      wintypes.HMONITOR,
                                      wintypes.HDC,
                                      ctypes.POINTER(wintypes.RECT),
                                      wintypes.LPARAM)


class _PHYSICAL_MONITOR(ctypes.Structure):
    _fields_ = [('hPhysicalMonitor', wintypes.HANDLE),
                ('szPhysicalMonitorDescription',
                 wintypes.WCHAR * _PHYSICAL_MONITOR_DESCRIPTION_SIZE)]


class MonitorData:
    def __init__(self, monitor_handle, device_id, rect):
        self.monitor_handle = monitor_handle
        self.device_id = device_id
        self.rect = rect


def get_displays():
    """Get a list of the available displays"""
    CCHDEVICENAME = 32

    def MonitorEnumProc_callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
        class MONITORINFOEX(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.wintypes.DWORD),
                        ("rcMonitor", ctypes.wintypes.RECT),
                        ("rcWork", ctypes.wintypes.RECT),
                        ("dwFlags", ctypes.wintypes.DWORD),
                        ("szDevice", ctypes.wintypes.WCHAR*CCHDEVICENAME)]
        lpmi = MONITORINFOEX()
        lpmi.cbSize = ctypes.sizeof(MONITORINFOEX)
        #win32api.GetMonitorInfo(hMonitor, ctypes.byref(lpmi))
        monitor_info = win32api.GetMonitorInfo(hMonitor)
        #hdc = self._gdi32.CreateDCA(ctypes.c_char_p(lpmi.szDevice), 0, 0, 0)
        #print('================== szDevice {}'.format(lpmi.szDevice))
        print('================== szDevice {}'.format(monitor_info))
        monitor = win32api.EnumDisplayDevices(monitor_info['Device'], 0)
        print('monitor DeviceID {}; handle {}; rect {}'.format(
            monitor.DeviceID, hMonitor, monitor_info['Monitor']))

        # lprcMonitor.contents matches monitor_info['Monitor']
        rct = lprcMonitor.contents
        print('        lprcMonitor (l t r b ) {} {} {} {}'.format(
            rct.left,
            rct.top,
            rct.right,
            rct.bottom))

        monitors.append(MonitorData(
            hMonitor, monitor.DeviceID, monitor_info['Monitor']))

        return True
    monitors = []
    displays = []
    # get display monitors
    if not ctypes.windll.user32.EnumDisplayMonitors(None, None,
                                                    _MONITORENUMPROC(MonitorEnumProc_callback), None):
        raise ctypes.WinError()

    # some debug
    i = 1
    for hMonitor, hdcMonitor, pyRect in win32api.EnumDisplayMonitors():
        monh = ctypes.wintypes.HANDLE()
        #print('{} monh {} {}'.format(i, monh, type(monh)))
        hMonitor = ctypes.wintypes.HANDLE(hMonitor.handle)
        print('{} hMonitor {} {}'.format(i, hMonitor, type(hMonitor)))
        i += 1

    # get physical monitors for each display monitor
    for monitor in monitors:
        monitor_number = wintypes.DWORD()
        ctypes.windll.dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR.argtypes = [
            wintypes.HMONITOR, wintypes.LPDWORD]
        if not ctypes.windll.dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR(
                monitor.monitor_handle, ctypes.byref(monitor_number)):
            raise ctypes.WinError()
        physical_monitor_array = (_PHYSICAL_MONITOR * monitor_number.value)()
        ctypes.windll.dxva2.GetPhysicalMonitorsFromHMONITOR.argtypes = [
            wintypes.HMONITOR, wintypes.DWORD, ctypes.POINTER(_PHYSICAL_MONITOR)]
        if not ctypes.windll.dxva2.GetPhysicalMonitorsFromHMONITOR(
                monitor.monitor_handle, monitor_number, physical_monitor_array):
            raise WinError()

        i = 1
        # print('{} hMonitor {} {}'.format(
        #    0, monitor.monitor_handle, type(monitor.monitor_handle)))
        for physical_monitor in physical_monitor_array:
            # print('{}/{} hMonitor {} {} {}'.format(i, monitor_number, physical_monitor.szPhysicalMonitorDescription,
            #                                       physical_monitor.hPhysicalMonitor, type(physical_monitor.hPhysicalMonitor)))
            i += 1

        for physical_monitor in physical_monitor_array:
            displays.append(CreateDisplay(monitor.monitor_handle, physical_monitor.hPhysicalMonitor,
                                          physical_monitor.szPhysicalMonitorDescription, monitor.device_id, monitor.rect))
    return displays


def CreateDisplay(monitorHandle, physicalMonitorHandle, physicalMonitorDescription, device_name, rect):
    _implementation = None

    # print(win32api.GetMonitorInfo(hMonitor))

    try:
        _implementation = DisplayVcp.DisplayVcp(
            monitorHandle, physicalMonitorHandle, device_name, rect)
        _implementation.capabilities

    except Exception as err:
        # print(err)
        # traceback.print_exc()
        _implementation = None

    if (_implementation is None):
        try:
            _implementation = Display.DisplayWmi(
                monitorHandle, physicalMonitorHandle, device_name, rect)
            _implementation.capabilities
        except Exception as err:
            print(err)
            traceback.print_exc()
            _implementation = None
    return _implementation
