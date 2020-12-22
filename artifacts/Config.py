

import sys  # We need sys so that we can pass argv to QApplication
import os


import Config
import Display
import Scaler
import yaml


class Calibration():
    def __init__(self, device_id):
        self.device_id = device_id
        self.scalers = {}

    def ensure(self, type):
        if (type not in self.scalers.keys()):
            self.scalers[type] = Scaler.Scaler([[0, 0], [100, 100]])

    def get(self, type):
        if (type in self.scalers.keys()):
            return self.scalers[type]
        return None

    def getYaml(self):
        opts = {}
        print('Calibration getYaml')
        for type, scaler in self.scalers.items():
            typeString = Display.Display.TypeToString(type)
            print('Calibration getYaml {}: {}'.format(
                typeString, scaler._scaling))
            opts[typeString] = scaler._scaling
        return self.device_id, opts

    def loadYaml(self, opts):
        print('Calibration loadYaml {}'.format(opts))
        for typeString, scaler in opts.items():
            type = Display.Display.StringToType(typeString)
            print('Calibration loadYaml {} {}: {}'.format(
                typeString, type, scaler))
            if (type is not None):
                self.scalers[type] = Scaler.Scaler(scaler)


# class Display():
#    CONTRAST = 1
#    BRIGHTNESS = 2
#    def TypeToString(argument):
#    def StringToType(argument):


class Calibrations():
    config_file = 'config.yaml'

    def __init__(self):
        self.calibrations = {}

    def get(self, device_id):
        if device_id not in self.calibrations.keys():
            self.calibrations[device_id] = Config.Calibration(device_id)
        return self.calibrations[device_id]

    def getYaml(self):
        opts = {}

        for id, calibration in self.calibrations.items():
            id, opt = calibration.getYaml()
            opts[id] = opt
        return {'Displays': opts}

    def saveYaml(self):
        print('\nsaveYaml:')
        print('saveYaml:\n{}'.format(self.getYaml()))
        with open(Calibrations.config_file, 'w') as f:
            data = yaml.dump(self.getYaml(), f)

    def loadYaml(self):
        if os.path.isfile(Calibrations.config_file):
            with open(Calibrations.config_file) as f:
                data = yaml.load(f, Loader=yaml.FullLoader)

            print('loadYaml:\n{}'.format(data))
            if (data is not None):
                if ('Displays' in data.keys()):
                    displays = data['Displays']
                    for device_id, opts in displays.items():
                        cal = self.get(device_id)
                        cal.loadYaml(opts)


def main():
    print("Config main")

    e = {'A':
         {'Brightness': [[0, 20], [50, 30], [100, 40]], 'Contrast': [[0, 20], [50, 30], [100, 40]]}}

    c = {'Displays':
         {'A':
          {'Brightness': [[0, 20], [50, 30], [100, 40]],
           'Contrast': [[0, 20], [50, 30], [100, 40]]},
          'B':
          {'Brightness': [[0, 20], [50, 30], [100, 40]],
           'Contrast': [[0, 20], [50, 30], [100, 40]]},
          'C':
          {'Brightness': [[0, 20], [50, 30], [100, 40]]}
          },
         'Last':
         {'Brightness': 80,
          'Contrast': 90}
         }

    print('c{}'.format(c))

    with open(Calibrations.config_file, 'w') as f:
        data = yaml.dump(c, f)

    with open(Calibrations.config_file) as f:

        data = yaml.load(f, Loader=yaml.FullLoader)
        print(data)

    cal = Config.Calibrations()
    cal.loadYaml()
    cal.saveYaml()


if __name__ == '__main__':
    main()
