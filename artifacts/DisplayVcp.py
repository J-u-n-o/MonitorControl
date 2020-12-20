
'''
import monitorcontrol

i = 0
for monitor in monitorcontrol.get_monitors():
    with monitor:
        print('Monitor {}; contrast {} luminance {}'.format(i, monitor.get_contrast(), monitor.get_luminance()))
        
        

#!/usr/bin/env python3

'''
"""
Show and adjust display parameters on a Dell U2713HM monitor
Requirements:
- mentioned monitor (27' should also work) with DDC/CI setting on
- Windows Vista+ (dxva2.dll)
- Python 3
Copyright (C) 2015  Diego Fernández Gosende <dfgosende@gmail.com>
Copyright (C) 2016  https://gist.github.com/Canule
Copyright (C) 2016  https://github.com/mchubby for Dell monitor
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License along 
with this program.  If not, see <http://www.gnu.org/licenses/gpl-3.0.html>.
"""


import Display
import wmi
import ctypes
import ctypes.wintypes as wintypes
import win32api
version = '0.1.0'


"""Capabilities string
prot(monitor)
type(lcd)
model(U2713HM)
cmds(01 02 03 07 0C E3 F3)
vcp(02 04 05 06 08 10 12 14(01 04 05 06 08 09 0B 0C) 16 18 1A 52
    60(01 03 04 0F) AC AE B2 B6 C6 C8 C9 D6(01 04 05) DC(00 02 03 05 )
    F0(00 01) DF FD E0 E1 E2(00 01 02 04 06 0B 0C 0D 0F 10 11 13 14) F1 F2)
mccs_ver(2.1)
mswhql(1))
"""

# Reference: VESA Monitor Control Command Set (MCCS)
# Standard PDF available after free registration
# at: http://www.vesa.org/vesa-standards/free-standards/

vcp_codes = {
    # ignore for scripting
    'New Control Value': 0x02,

    # pass a non-zero value
    'Restore Factory Defaults': 0x04,

    # pass a non-zero value
    'Restore Factory Luminance/ Contrast Defaults': 0x05,

    # pass a non-zero value
    'Restore Factory Geometry Defaults': 0x06,

    # pass a non-zero value, resets also luminance
    'Restore Factory Color Defaults': 0x08,

    # 0-100, called 'brightness' on the OSD
    'Luminance': 0x10,

    # 0-100
    'Contrast': 0x12,

    # 0x01: sRGB
    # 0x04: 5000k
    # 0x05: 6500k
    # 0x06: 7500k
    # 0x08: 9300k
    # 0x09: 10000k
    # 0x0B: 5700k
    # 0x0C: user (Custom Color)
    'Select Color Preset': 0x14,

    # 0-100, it also changes the preset to 'user'
    'Video Gain (Drive): Red': 0x16,

    # 0-100, it also changes the preset to 'user'
    'Video Gain (Drive): Green': 0x18,

    # 0-100, it also changes the preset to 'user'
    'Video Gain (Drive): Blue': 0x1A,

    # ignore for scripting
    'Active Control': 0x52,

    # 0x01: VGA, 0x03: DVI, 0x04: HDMI, 0x0F: DisplayPort
    'Input Source': 0x60,

    # 0-100 (unexposed command)
    'Video Black Level: Red': 0x16,

    # 0-100 (unexposed command)
    'Video Black Level: Green': 0x18,

    # 0-100 (unexposed command)
    'Video Black Level: Blue': 0x1A,

    # read-only, Hz
    'Horizontal Frequency': 0xAC,

    # read-only, 0.01 Hz
    'Vertical Frequency': 0xAE,

    # read-only, 0x01 -> Red / Green / Blue vertical stripe
    'Flat Panel Sub-Pixel Layout': 0xB2,

    # read-only, 0x03 -> LCD (active matrix)
    'Display Technology Type': 0xB6,

    # read-only, 0x6f, some id
    'Application Enable Key': 0xC6,

    # read-only, 0x5605 -> Mstar Semiconductor
    'Display Controller Type': 0xC8,

    # read-only, 0x0101
    'Display Firmware Level': 0xC9,

    # 01 or 02 (unexposed command)
    'OSD': 0xCA,

    # 0x01: power on, 0x04: standby (screenoff + blinking led), 0x05: power off
    'Power Mode': 0xD6,

    # presets (manufacturer-defined):
    # no Text preset?
    # 00: Standard
    # 02: Mixed (Multimedia)
    # 03: Movie
    # 05: Games
    'Display Application': 0xDC,

    # read-only, 0x0201 -> MCCS v2.1
    'VCP Version': 0xDF,

    # Codes 0xE0 to 0xFF are manufacturer-specific

    # ignore for scripting, 00 or 01 (Energy Smart?)
    'Dell-E0': 0xE0,

    # ignore for scripting
    # power control
    # 01: off
    # 00: on
    'Dell-E1': 0xE1,

    # ignore for scripting, 00 01 02 04 06 0B 0C 0D 0F 10 11 13 14
    'Dell-E2': 0xE2,

    # ignore for scripting, 00 or 01 (magicbright?)
    'Dell-F0': 0xF0,

    # ignore for scripting, read
    'Dell-F1': 0xF1,

    # ignore for scripting, read-only, (Energy Smart?)
    'Dell-F2': 0xF2,

    # ignore for scripting
    'Dell-FD': 0xFD,
}


class DisplayVcp(Display.Display):

    def __init__(self, monitorHandle, physicalMonitorHandle, device_name, rect):
        print("DisplayVcp {}".format(device_name))
        Display.Display.__init__(
            self, monitorHandle, physicalMonitorHandle, device_name, rect)
        self._capabilities = None

    @property
    def capabilities(self):
        if self._capabilities is None:
            self._get_capabilities()
        return self._capabilities

    @property
    def capabilities_raw(self):
        if self._capabilities_raw is None:
            self._get_capabilities()
        return self._capabilities_raw

    def _get_capabilities(self):
        # print("Vcp1:{}".format(wmi.WMI(namespace='wmi').WmiMonitorID()[1]))
        # this is slow
        length = wintypes.DWORD()
        if not ctypes.windll.dxva2.GetCapabilitiesStringLength(
                self._physicalMonitorHandle, ctypes.byref(length)):
            raise ctypes.WinError()
        capabilities_string = (ctypes.c_char * length.value)()
        if not ctypes.windll.dxva2.CapabilitiesRequestAndCapabilitiesReply(
                self._physicalMonitorHandle, capabilities_string, length):
            raise ctypes.WinError()
        self._capabilities_raw = capabilities_string.value.decode('ascii')
        self._capabilities = self.parse_capabilities_string(
            self._capabilities_raw)

    @classmethod
    def parse_capabilities_string(cls, capabilities_string):
        level = 0
        capabilities = {}
        open_p = {}
        close_p = {0: 0}
        id = {}
        for i, chr in enumerate(capabilities_string):
            if chr == '(':
                if i == 0:
                    close_p[0] = 1
                    continue
                open_p[level] = i
                if level == 0:
                    id[0] = capabilities_string[close_p[0] + 1:i]
                level += 1
            elif chr == ')':
                level -= 1
                close_p[level] = i
                if level == 0:
                    values = capabilities_string[open_p[0] + 1:i]
                    if id[0] == 'cmds':
                        values = values.split()
                    elif id[0] == 'vcp':
                        values = cls._parse_vcp_list(values)
                    capabilities[id[0]] = values
        return capabilities

    @staticmethod
    def _parse_vcp_list(vcp_list):
        vcp_dict = {}
        open_p = 0
        for i, chr in enumerate(vcp_list):
            if chr == '(':
                open_p = i
                code = vcp_list[i-2:i]
            elif chr == ')':
                vcp_dict[code] = vcp_list[open_p + 1:i].split()
            elif chr.isspace() and vcp_list[i-1] != ')':
                vcp_dict[vcp_list[i-2:i]] = None
        return vcp_dict

    def _get_vcf_feature_and_vcf_feature_reply(self, code):
        """Get current and maximun values for continuous VCP codes"""
        current_value = wintypes.DWORD()
        maximum_value = wintypes.DWORD()
        if not ctypes.windll.dxva2.GetVCPFeatureAndVCPFeatureReply(
                self._physicalMonitorHandle, wintypes.BYTE(code), None,
                ctypes.byref(current_value),
                ctypes.byref(maximum_value)):
            raise ctypes.WinError()
        return current_value.value, maximum_value.value

    def _set_vcp_feature(self, code, value):
        """Set 'code' to 'value'"""
        if not ctypes.windll.dxva2.SetVCPFeature(self._physicalMonitorHandle,
                                                 wintypes.BYTE(code), wintypes.DWORD(value)):
            raise ctypes.WinError()

    @property
    def model(self):
        return self.capabilities['model']

    _display_technology_types = {
        0x01: 'CRT (shadow mask)',
        0x02: 'CRT (aperture grill)',
        0x03: 'LCD (active matrix)',
        0x04: 'LCoS',
        0x05: 'Plasma',
        0x06: 'OLED',
        0x07: 'EL',
        0x08: 'Dynamic MEM e.g. DLP',
        0x09: 'Static MEM e.g. iMOD', }

    @property
    def display_technology_type(self):
        return self._display_technology_types.get(
            self._get_vcf_feature_and_vcf_feature_reply(
                vcp_codes['Display Technology Type'])[0])

    _flat_panel_sub_pixel_layouts = {
        0x00: 'Sub-pixel layout is not defined',
        0x01: 'Red / Green / Blue vertical stripe',
        0x02: 'Red / Green / Blue horizontal stripe',
        0x03: 'Blue / Green / Red vertical stripe',
        0x04: 'Blue/ Green / Red horizontal stripe',
        0x05: 'Quad-pixel, a 2 x 2 sub-pixel structure with red at top left, '
              'blue at bottom right and green at top right and bottom left',
        0x06: 'Quad-pixel, a 2 x 2 sub-pixel structure with red at bottom '
              'left, blue at top right and green at top left and bottom right',
        0x07: 'Delta (triad)',
        0x08: 'Mosaic with interleaved sub-pixels of different colors', }

    @property
    def flat_panel_sub_pixel_layout(self):
        return self._flat_panel_sub_pixel_layouts.get(
            self._get_vcf_feature_and_vcf_feature_reply(
                vcp_codes['Flat Panel Sub-Pixel Layout'])[0])

    _display_controller_type_lsb = {
        0x01: 'Conexant',
        0x02: 'Genesis Microchip',
        0x03: 'Macronix',
        0x04: 'MRT (Media Reality Technologies)',
        0x05: 'Mstar Semiconductor',
        0x06: 'Myson',
        0x07: 'Philips',
        0x08: 'PixelWorks',
        0x09: 'RealTek Semiconductor',
        0x0A: 'Sage',
        0x0B: 'Silicon Image',
        0x0C: 'SmartASIC',
        0x0D: 'STMicroelectronics',
        0x0E: 'Topro',
        0x0F: 'Trumpion',
        0x10: 'Welltrend',
        0x11: 'Samsung',
        0x12: 'Novatek Microelectronics',
        0x13: 'STK',
        0xFF: 'Manufacturer designed controller', }

    @property
    def display_controller_type(self):
        value = self._get_vcf_feature_and_vcf_feature_reply(
            vcp_codes['Display Controller Type'])[0]
        return self._display_controller_type_lsb.get(value & 0xff)

    @property
    def display_firmware_level(self):
        value = self._get_vcf_feature_and_vcf_feature_reply(
            vcp_codes['Display Firmware Level'])[0]
        return '{}.{}'.format(value >> 8, value & 0x1f)

    @property
    def application_enable_key(self):
        return self._get_vcf_feature_and_vcf_feature_reply(
            vcp_codes['Application Enable Key'])[0]

    @property
    def vcp_version(self):
        value = self._get_vcf_feature_and_vcf_feature_reply(
            vcp_codes['VCP Version'])[0]
        return '{}.{}'.format(value >> 8, value & 0xff)

    @property
    def vertical_frequency(self):
        return self._get_vcf_feature_and_vcf_feature_reply(
            vcp_codes['Vertical Frequency'])[0] / 100

    @property
    def horizontal_frequency(self):
        value = self._get_vcf_feature_and_vcf_feature_reply(
            vcp_codes['Horizontal Frequency'])[0]
        if value < 50000:  # MSB is missing, should be 0 or 1
            value |= 0x10000
        return value / 1000

    @property
    def brightness(self):
        return self._get_vcf_feature_and_vcf_feature_reply(
            vcp_codes['Luminance'])[0]

    @brightness.setter
    def brightness(self, value):
        current, max = self._get_vcf_feature_and_vcf_feature_reply(
            vcp_codes['Luminance'])
        if value == current:
            return
        if value > max:
            value = max
        elif value < 0:
            value = 0
        self._set_vcp_feature(vcp_codes['Luminance'], int(value))

    @property
    def max_brightness(self):
        return self._get_vcf_feature_and_vcf_feature_reply(
            vcp_codes['Luminance'])[1]

    @property
    def contrast(self):
        return self._get_vcf_feature_and_vcf_feature_reply(
            vcp_codes['Contrast'])[0]

    @contrast.setter
    def contrast(self, value):
        current, max = self._get_vcf_feature_and_vcf_feature_reply(
            vcp_codes['Contrast'])
        if int(value) == current:
            return
        if value > max:
            value = max
        elif value < 0:
            value = 0
        self._set_vcp_feature(vcp_codes['Contrast'], int(value))

    @property
    def max_contrast(self):
        return self._get_vcf_feature_and_vcf_feature_reply(
            vcp_codes['Contrast'])[1]

    @property
    def color_temperature(self):
        value = self._get_vcf_feature_and_vcf_feature_reply(
            vcp_codes['Color Temperature Request'])[0]
        increment = self._get_vcf_feature_and_vcf_feature_reply(
            vcp_codes['Color Temperature Increment'])[0]
        return 3000 + increment * value

    @color_temperature.setter
    def color_temperature(self, value):
        current, max = self._get_vcf_feature_and_vcf_feature_reply(
            vcp_codes['Color Temperature Request'])
        increment = self._get_vcf_feature_and_vcf_feature_reply(
            vcp_codes['Color Temperature Increment'])[0]
        value = (value - 3000) // increment
        if value == current:
            return
        if value > max:
            value = max
        elif value < 0:
            value = 0
        self._set_vcp_feature(vcp_codes['Color Temperature Request'], value)

    @property
    def max_color_temperature(self):
        value = self._get_vcf_feature_and_vcf_feature_reply(
            vcp_codes['Color Temperature Request'])[1]
        increment = self._get_vcf_feature_and_vcf_feature_reply(
            vcp_codes['Color Temperature Increment'])[0]
        return 3000 + increment * value

    _color_presets = {0x01: 'srgb', 0x04: '5000k', 0x05: '6500k',
                      0x06: '7500k', 0x08: '9300k', 0x09: '10000k',
                      0x0B: '5700k', 0x0C: 'user'}
    _color_presets_i = {'srgb': 0x01, '5000k': 0x04, '6500k': 0x05,
                        '7500k': 0x06, '9300k': 0x08, '10000k': 0x09,
                        '5700k': 0x0B, 'user': 0x0C}

    @property
    def color_preset(self):
        value = self._get_vcf_feature_and_vcf_feature_reply(
            vcp_codes['Select Color Preset'])[0]
        return self._color_presets[value]

    @color_preset.setter
    def color_preset(self, value):
        value = self._color_presets_i[value]
        if value == self._get_vcf_feature_and_vcf_feature_reply(
                vcp_codes['Select Color Preset'])[0]:
            return
        self._set_vcp_feature(vcp_codes['Select Color Preset'], value)

    @property
    def rgb(self):
        return [self._get_vcf_feature_and_vcf_feature_reply(
            vcp_codes['Video Gain (Drive): {}'.format(color)])[0]
            for color in ['Red', 'Green', 'Blue']]

    @rgb.setter
    def rgb(self, values):
        color = ['Red', 'Green', 'Blue']
        template = 'Video Gain (Drive): {}'
        for i, value in enumerate(values):
            vcp_name = template.format(color[i])
            current, max = self._get_vcf_feature_and_vcf_feature_reply(
                vcp_codes[vcp_name])
            if value in (-1, current):
                continue
            if value > max:
                value = max
            elif value < 0:
                value = 0
            self._set_vcp_feature(vcp_codes[vcp_name], value)

    @property
    def max_rgb(self):
        return [self._get_vcf_feature_and_vcf_feature_reply(
            vcp_codes['Video Gain (Drive): {}'.format(color)])[1]
            for color in ['Red', 'Green', 'Blue']]

    _input_sources = {0x01: 'vga', 0x03: 'dvi', 0x04: 'hdmi', 0x0F: 'dp'}
    _input_sources_i = {'vga': 0x01, 'dvi': 0x03, 'hdmi': 0x04, 'dp': 0x0F}

    @property
    def input_source(self):
        value = self._get_vcf_feature_and_vcf_feature_reply(
            vcp_codes['Input Source'])[0]
        return self._input_sources[value]

    @input_source.setter
    def input_source(self, value):
        value = self._input_sources_i[value]
        if value == self._get_vcf_feature_and_vcf_feature_reply(
                vcp_codes['Input Source'])[0]:
            return
        self._set_vcp_feature(vcp_codes['Input Source'], value)

    _display_applications = {0x00: 'std',
                             0x02: 'mix', 0x03: 'mov', 0x05: 'gam'}
    _display_applications_i = {'std': 0x00,
                               'mix': 0x02, 'mov': 0x03, 'gam': 0x05}

    @property
    def display_application(self):
        value = self._get_vcf_feature_and_vcf_feature_reply(
            vcp_codes['Display Application'])[0]
        return self._display_applications[value]

    @display_application.setter
    def display_application(self, value):
        value = self._display_applications_i[value]
        if value == self._get_vcf_feature_and_vcf_feature_reply(
                vcp_codes['Display Application'])[0]:
            return
        self._set_vcp_feature(vcp_codes['Display Application'], value)

    _power_mode = {0x01: 'on', 0x05: 'off'}
    _power_mode_i = {'on': 0x01, 'off': 0x05}

    @property
    def power_mode(self):
        value = self._get_vcf_feature_and_vcf_feature_reply(
            vcp_codes['Power Mode'])[0]
        return self._power_mode[value]

    @power_mode.setter
    def power_mode(self, value):
        value = self._power_mode_i[value]
        if value == self._get_vcf_feature_and_vcf_feature_reply(
                vcp_codes['Power Mode'])[0]:
            return
        self._set_vcp_feature(vcp_codes['Power Mode'], value)

    _restore_options = {
        'all': 'Restore Factory Defaults',
        'luminance': 'Restore Factory Luminance/ Contrast Defaults',
        'color': 'Restore Factory Color Defaults'}

    def restore(self, option):
        """Restore factory defaults ('all' / 'luminance' / 'colors')"""
        self._set_vcp_feature(vcp_codes[self._restore_options[option]], 1)

    def close(self):
        if not ctypes.windll.dxva2.DestroyPhysicalMonitor(self._physicalMonitorHandle):
            raise ctypes.WinError()

    def __del__(self):
        self.close()


if __name__ == '__main__':

    import sys
    import os
    import argparse
    import textwrap

    # Custom Action for argparse
    # The accepted number of arguments can be specified with '_nargs' (list)
    # 'nargs' must be '*'
    # Added also 'default_str' and 'const_str', formatted with 'default' and
    # 'const' respectively, that can be used on the 'help' string

    class VariableNArgsAction(argparse.Action):

        def __init__(self, option_strings, dest, **kwargs):
            self._nargs = kwargs.pop('_nargs', None)
            self.const_str = kwargs.pop('const_str', None)
            self.default_str = kwargs.pop('default_str', None)
            argparse.Action.__init__(self, option_strings, dest, **kwargs)
            if self.const_str is not None:
                self.const_str = self.const_str.format(*self.const)
            if self.default_str is not None:
                self.default_str = self.default_str.format(*self.default)

        def __call__(self, parser, namespace, values, option_string=None):
            if len(values) not in self._nargs:
                parser.error('argument {}: invalid number of arguments'
                             .format('/'.join(self.option_strings)))
            if not values and self.const is not None:
                values = self.const
            setattr(namespace, self.dest, values)

    # For VariableNArgsAction, use 'metavar' as the displayed args string
    # XXX: not part of the public API

    class RawDescriptionHelpFormatter2(argparse.RawDescriptionHelpFormatter):

        def _format_args(self, action, *args, **kwargs):
            if action.metavar is not None and isinstance(action,
                                                         VariableNArgsAction):
                return action.metavar
            return argparse.RawDescriptionHelpFormatter._format_args(
                self, action, *args, **kwargs)

    # Set / show display parameters
    for display in get_displays():
        try:
            model = display.capabilities['model']
            print(textwrap.dedent('''\
                model: {model}
                '''.format(model=model, display=display)))
            print(display.capabilities)
        except Exception as err:
            print(err)
            traceback.print_exc()

        try:
            print(textwrap.dedent('''\
                model: {model}
                display technology type: {display.display_technology_type}
                flat panel sub-pixel layout: {display.flat_panel_sub_pixel_layout}
                display controller type: {display.display_controller_type}
                display firmware level: v{display.display_firmware_level}
                application enable key: {display.application_enable_key}
                vcp version: v{display.vcp_version}
                vertical frequency: {display.vertical_frequency} Hz
                horizontal frequency: {display.horizontal_frequency} kHz
                
                brightness: {display.brightness}
                contrast {display.contrast}
                color preset: {display.color_preset}
                rgb gains: {display.rgb}
                input source: {display.input_source}
                power mode: {display.power_mode}
                '''.format(model=model, display=display)))
        except Exception as err:
            print(err)
            traceback.print_exc()
