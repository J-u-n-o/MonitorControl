
import Display

import wmi
import win32api
import ctypes
import ctypes.wintypes as wintypes
import win32api

import traceback
import string
import Scaler

from win32com.client import GetObject
import win32com

import Display


def _get_id(address):
    address.replace('\\\\', '\\')
    address_parts = address.split('\\')
    # print("_get_id: {}:{}".format(address, address_parts))
    return address_parts[1]


def wmi_to_string(obj_string):
    _objs_string = ''.join(
        chr(i) for i in obj_string).strip()
    _objs_string = ''.join(
        [x for x in _objs_string if x in string.printable])
    _objs_string = _objs_string.strip()
    return _objs_string


def del_trailing_zeros(mylist):
    for i, j in enumerate(reversed(mylist)):
        if (0 != j):
            mylist = mylist[:-1*i]
            break
    return mylist


def wmi_to_hex_string(obj_ids):
    return '0x' + ''.join('{:02x}'.format(x) for x in del_trailing_zeros(obj_ids))


class Display():
    CONTRAST = 1
    BRIGHTNESS = 2

    @staticmethod
    def TypeToString(argument):
        types = {
            1: "Contrast",
            2: "Brightness",
        }
        print('TypeToString {} -> {}'.format(argument, types.get(argument, None)))
        return types.get(argument, None)

    @staticmethod
    def StringToType(argument):
        i = 1
        t = Display.TypeToString(i)
        while t is not None:
            if argument.strip().lower() == t.strip().lower():
                return i
            i += 1
            t = Display.TypeToString(i)
        return None

    def __init__(self, monitorHandle, physicalMonitorHandle, device_name, rect):
        self._monitorHandle = monitorHandle
        self._physicalMonitorHandle = physicalMonitorHandle
        self._rect = rect

        # example: MONITOR\CMN14C9\{4d36e96e-e325-11ce-bfc1-08002be10318}\0001
        self._device_name = device_name

        # example: DISPLAY\\CMN14C9\\4&cccf5b5&0&UID265988_0
        self._wmi_instance_name = None
        self._wmi_monitor_index = 0
        # part of both _device_name and _wmi_instance_name to match monitor handle and WMI interfaces
        self._id = _get_id(self._device_name)

        self.wmi = {}
        self.info = {}
        self._get_wmi_monitor()

        # self._print_capabilities()

    def _match_address(self, address):
        id = _get_id(address)
        return (self._id == id)

    def _get_wmi_monitor(self):
        objWMI = win32com.client.GetObject(
            'winmgmts:\\\\.\\root\\WMI').InstancesOf('WmiMonitorID')
        # print("Id: {}".format(self._id))

        index = -1
        for obj in objWMI:
            index += 1
            if (self._match_address(obj.InstanceName)):
                self._index = index
                # print("Index:" + str(self._index))
                if obj.UserFriendlyName != None:
                    userFriendlyName = ''.join(chr(i)
                                               for i in obj.UserFriendlyName)
                    userFriendlyName = ''.join(
                        [x for x in userFriendlyName if x in string.printable])
                    userFriendlyName = userFriendlyName.strip()
                    self.wmi['UserFriendlyName'] = wmi_to_string(
                        obj.userFriendlyName)
                    self.info['Name'] = wmi_to_string(
                        obj.userFriendlyName)
                #    print("UserFriendlyName:" + userFriendlyName +
                #          str(obj.UserFriendlyName))
                #
                # if obj.UserFriendlyNameLength != None:
                #    self.wmi['ManufacturerName'] = manufacturerName
                #    print("UserFriendlyNameLength:" +
                #          str(obj.UserFriendlyNameLength))
                if obj.Active != None:
                    self.wmi['Active'] = str(obj.Active)
                    self.info['Active'] = str(obj.Active)
                #    print("Active:" + str(obj.Active))
                if obj.InstanceName != None:
                    self.wmi['InstanceName'] = str(obj.InstanceName)
                    self.info['Instance'] = str(obj.InstanceName)
                #    print("InstanceName:" + str(obj.InstanceName))
                self.info['WindowArea'] = '{}, {}; {} x {} (x, y; w x h)'.format(
                    self._rect[0], self._rect[1], self._rect[2] - self._rect[0], self._rect[3] - self._rect[1])
                if obj.ManufacturerName != None:
                    manufacturerName = ''.join(
                        chr(i) for i in obj.ManufacturerName).strip()
                    manufacturerName = ''.join(
                        [x for x in manufacturerName if x in string.printable])
                    manufacturerName = manufacturerName.strip()
                    self.wmi['ManufacturerName'] = wmi_to_string(
                        obj.manufacturerName)
                    self.info['Manufacturer'] = wmi_to_string(
                        obj.manufacturerName)
                #    print("ManufacturerName:'" + manufacturerName +
                #          "'" + str(obj.ManufacturerName))
                if obj.ProductCodeID != None:
                    self.wmi['ProductCodeID'] = wmi_to_hex_string(
                        obj.ProductCodeID)
                    self.wmi['ProductCodeID_readable'] = wmi_to_string(
                        obj.ProductCodeID)
                    self.info['ProductCodeID'] = wmi_to_string(
                        obj.ProductCodeID)
                #    print("ProductCodeID:" + str(obj.ProductCodeID))
                if obj.SerialNumberID != None:
                    self.wmi['SerialNumberID'] = wmi_to_hex_string(
                        obj.SerialNumberID)
                    self.wmi['SerialNumberID_readable'] = wmi_to_string(
                        obj.SerialNumberID)
                    self.info['SerialNumber'] = wmi_to_string(
                        obj.SerialNumberID)
                #    print("SerialNumberID:" + str(obj.SerialNumberID))
                if obj.WeekOfManufacture != None:
                    self.wmi['WeekOfManufacture'] = str(obj.WeekOfManufacture)
                #    print("WeekOfManufacture:" + str(obj.WeekOfManufacture))
                if obj.YearOfManufacture != None:
                    self.wmi['YearOfManufacture'] = str(obj.YearOfManufacture)
                #    print("YearOfManufacture:" + str(obj.YearOfManufacture))
                # print("")
                # print("########")
                # print("")

    def _print_capabilities(self):
        objWMI = win32com.client.GetObject(
            'winmgmts:\\\\.\\root\\WMI').InstancesOf('WmiMonitorID')
        print("Id: {}".format(self._id))

        index = -1
        for obj in objWMI:
            index += 1
            if (self._match_address(obj.InstanceName)):
                self._index = index
                print("Index:" + str(self._index))
                if obj.Active != None:
                    print("Active:" + str(obj.Active))
                if obj.InstanceName != None:
                    print("InstanceName:" + str(obj.InstanceName))
                if obj.ManufacturerName != None:
                    manufacturerName = ''.join(
                        chr(i) for i in obj.ManufacturerName).strip()
                    manufacturerName = manufacturerName.strip()
                    print("ManufacturerName:'" + manufacturerName +
                          "'" + str(obj.ManufacturerName))
                if obj.ProductCodeID != None:
                    print("ProductCodeID:" + str(obj.ProductCodeID))
                if obj.SerialNumberID != None:
                    print("SerialNumberID:" + str(obj.SerialNumberID))
                if obj.UserFriendlyName != None:
                    userFriendlyName = ''.join(chr(i)
                                               for i in obj.UserFriendlyName)
                    userFriendlyName = userFriendlyName.strip()
                    print("UserFriendlyName:" + userFriendlyName +
                          str(obj.UserFriendlyName))

                if obj.UserFriendlyNameLength != None:
                    print("UserFriendlyNameLength:" +
                          str(obj.UserFriendlyNameLength))
                if obj.WeekOfManufacture != None:
                    print("WeekOfManufacture:" + str(obj.WeekOfManufacture))
                if obj.YearOfManufacture != None:
                    print("YearOfManufacture:" + str(obj.YearOfManufacture))
                print("")
                print("########")
                print("")


class DisplayWmi(Display):

    def __init__(self, monitorHandle, physicalMonitorHandle, device_name, rect):
        print("DisplayWmi {}".format(device_name))
        # print('i')
        Display.__init__(self, monitorHandle,
                         physicalMonitorHandle, device_name, rect)
        self._capabilities = None

    @property
    def capabilities(self):
        # print('j')
        if self._capabilities is None:
            self._get_capabilities()
        return self._capabilities

    def _get_capabilities(self):
        # print('k')
        self._capabilities = {'model': 'WMI'}
        # print('l')
        self._capabilities['model'] = 'WMI'
        # print('brightness {}'.format(self.brightness))
        # print("Wmi1:{}".format(
        #     wmi.WMI(namespace='wmi').WmiMonitorID()[self._index]))
        # print("1:{}".format(wmi.WMI(namespace='wmi').WmiMonitorDescriptorMethods()[0]))
        # print("1:{}".format(wmi.WMI(namespace='wmi').WmiMonitorID()))
        # print("1:{}".format(wmi.WMI(namespace='wmi').WmiMonitorBrightness()))
        # print("1:{}".format(
        #     wmi.WMI(namespace='wmi').WmiMonitorBasicDisplayParams()[self._index]))
        # print("1:{}".format(
        #     wmi.WMI(namespace='wmi').WmiMonitorColorCharacteristics()[self._index]))
        # print("1:{}".format(wmi.WMI(namespace='wmi').SupportedDisplayFeaturesDescriptor()[0]))

    @property
    def brightness(self):
        b = None
        for obj in wmi.WMI(namespace='wmi').WmiMonitorBrightness():
            if (self._match_address(obj.InstanceName)):
                # print('WMI brightness: {}'.format(obj))
                b = obj.CurrentBrightness
                # print('Level: {}'.format(type(obj.Level)))
                self._brightness_levels = Scaler.Level(list(obj.Level))

        return b

    @brightness.setter
    def brightness(self, value):
        # get first before setting so level are obtained
        b = self.brightness
        for obj in wmi.WMI(namespace='wmi').WmiMonitorBrightnessMethods():
            if (self._match_address(obj.InstanceName)):
                desired_brightness = self._brightness_levels._get(value)
                obj.WmiSetBrightness(desired_brightness, 0)
                b = self.brightness

                print('WMI {} : brightness {} -> {} : {}'.format(self._id,
                                                                 value, desired_brightness, b))

    @property
    def contrast(self):
        b = None
        return b

    @contrast.setter
    def contrast(self, value):
        # get first before setting so level are obtained
        print('WMI {} : contrast {} not supported'.format(self._id,
                                                          value))


def main():
    print("Display main")
    print('{}'.format(Display.Display.BRIGHTNESS))


if __name__ == '__main__':
    main()
