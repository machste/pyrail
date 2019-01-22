class Version(object):

    def __init__(self, version=None):
        self.version = version

    @property
    def array(self):
        return self._array

    @property
    def appendix(self):
        return self._appendix

    @property
    def version(self):
        return str(self)

    @version.setter
    def version(self, version):
        self.parse(version)

    def is_null(self):
        for number in self._array:
            if number != 0:
                return False
        return True

    def parse(self, version):
        ret = True
        if isinstance(version, Version):
            self._array = version._array
            self._appendix = version._appendix
        else:
            self._array = [0] * 2
            self._appendix = ""
            if version is None:
                pass
            elif type(version) == str:
                version_parts = version.split("-")
                version = version_parts[0].split(".")
                if len(version_parts) > 1:
                    self._appendix = "-" + version_parts[1]
            if type(version) == list:
                self._array = list(map(int, version))
            else:
                raise TypeError("Unable to convert %s to a Version object" %
                        type(version))
        return ret

    def __len__(self):
        return len(self._array)

    def _at_idx(self, idx):
        try:
            return self._array[idx]
        except IndexError:
            return 0

    @staticmethod
    def _cmp_appendix(x, y):
        if len(x) == 0 and len(y) > 0:
            return 1
        elif len(x) > 0 and len(y) == 0:
            return -1
        else:
            return (x > y) - (x < y)

    def __cmp__(self, other):
        if isinstance(other, Version):
            # Compare version number one by one
            for i in range(max(len(self._array), len(other._array))):
                a, b = self._at_idx(i), other._at_idx(i)
                if a == b:
                    continue
                else:
                    return a - b
            # If the version numbers are equal compare the appendix
            return self._cmp_appendix(self._appendix, other._appendix)
        else:
            raise TypeError("Unable to compare %s with Version!" % type(other))

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __ne__(self, other):
        return self.__cmp__(other) != 0

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __le__(self, other):
        return self.__cmp__(other) <= 0

    def __gt__(self, other):
        return self.__cmp__(other) > 0

    def __ge__(self, other):
        return self.__cmp__(other) >= 0

    def __str__(self):
        return ".".join(map(str, self._array)) + self._appendix
