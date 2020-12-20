

class Scaler():
    def __init__(self, scaling):
        self._set(scaling)

    def _set(self, scaling):
        self._scaling = scaling
        self._scaling0 = scaling
        self._scaling1 = scaling
        self._scaling0.sort(key=lambda x: x[0])
        self._scaling1.sort(key=lambda x: x[1])

    def _get(self, value):
        if (self._scaling is None):
            return None

        previous_row = None
        current_row = None
        for row in self._scaling0:
            # print('row {} {}'.format(row[0], row[1]))
            if (row[0] > value):
                if (current_row is None):
                    current_row = row
                break
            if (row[0] >= value):
                current_row = row
            if ((previous_row is None) or (row[0] - previous_row[0]) >= 0.0001):
                previous_row = row

        if (previous_row is None):
            return self._scaling0[0][1]
        if (current_row is None):
            return previous_row[1]

        if ((current_row[0] - previous_row[0]) < 0.0001):
            return ((previous_row[1] + current_row[1]) / 2)

        return (previous_row[1] + ((current_row[1] - previous_row[1]) *
                                   (value - previous_row[0]) / (current_row[0] - previous_row[0])))

    def _get_inv(self, value):
        if (self._scaling is None):
            return None

        previous_row = None
        current_row = None
        for row in self._scaling1:
            # print('row {} {}'.format(row[0], row[1]))
            if (row[1] > value):
                if (current_row is None):
                    current_row = row
                break
            if (row[1] >= value):
                current_row = row
            if ((previous_row is None) or ((row[1] - previous_row[1]) >= 0.0001)):
                previous_row = row

        if (previous_row is None):
            return int(self._scaling1[0][0])
        if (current_row is None):
            return int(previous_row[0])

        if ((current_row[1] - previous_row[1]) < 0.0001):
            return int((previous_row[0] + current_row[0]) / 2)

        return int(previous_row[0] + ((current_row[0] - previous_row[0]) *
                                      (value - previous_row[1]) / (current_row[1] - previous_row[1])))


class Level():
    def __init__(self, levels=[]):
        self._levels = levels
        self._levels.sort()

    def add(self, level):
        self._levels.append(level)
        self._levels.sort()

    def _get(self, value):
        if (self._levels is None):
            return None

        previous_level = None
        current_level = None
        for level in self._levels:
            if (level > value):
                if (current_level is None):
                    current_level = level
                break
            if (level >= value):
                current_level = level
            if ((previous_level is None) or (level - previous_level >= 0.0001)):
                previous_level = level

        if (previous_level is None):
            return int(self._levels[0])
        if (current_level is None):
            return int(previous_level)

        if ((value - previous_level) < (current_level - value)):
            return int(previous_level)

        return int(current_level)


def get_value_from(value, levels):
    return value


if __name__ == '__main__':

    #level = Level([10, 0, 90, 50, 100])
    level = Level()
    level.add(10)
    level.add(0)
    level.add(90)
    level.add(50)
    level.add(100)
    print('level {}'.format(level._levels))
    print('level -1 {}'.format(level._get(-1)))
    print('level 0 {}'.format(level._get(0)))
    print('level 5 {}'.format(level._get(5)))
    print('level 10 {}'.format(level._get(10)))
    print('level 15 {}'.format(level._get(15)))
    print('level 29.0 {}'.format(level._get(29.0)))
    print('level 30 {}'.format(level._get(30)))
    print('level 30.1 {}'.format(level._get(30.1)))

    exit()

    scaler = Scaler([[0, 0], [90, 100], [50, 0], [75, 25],
                     [75, 50], [75, 75], [100, 100]])

    print('scaler {}'.format(scaler._scaling))
    print('scaler {}'.format(scaler._scaling0))
    print('scaler 75 {}'.format(scaler._get(75)))

    exit()
    print('scaler -20 {}'.format(scaler._get(-20)))
    print('scaler 20 {}'.format(scaler._get(20)))
    print('scaler  5 {}'.format(scaler._get(5)))
    print('scaler 10 {}'.format(scaler._get(10)))

    print('scaler 89 {}'.format(scaler._get(89)))
    print('scaler 91 {}'.format(scaler._get(91)))
    print('scaler 120 {}'.format(scaler._get(120)))

    print('scaler {}'.format(scaler._scaling1))
    print('scaler -20 {}'.format(scaler._get_inv(-20)))
    print('scaler 20 {}'.format(scaler._get_inv(20)))
    print('scaler 10 {}'.format(scaler._get_inv(10)))
    print('scaler 50 {}'.format(scaler._get_inv(50)))
    print('scaler 89 {}'.format(scaler._get_inv(89)))
    print('scaler 99 {}'.format(scaler._get_inv(99)))
    print('scaler 120 {}'.format(scaler._get_inv(120)))
