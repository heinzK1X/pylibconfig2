#TODO: license here?


class ConfError(Exception):
    pass


class _ListType(list):
    l_delim = ""
    r_delim = ""

    def __init__(self, ini_list=None):
        if ini_list:
            for k in ini_list:
                self.append(k)

    def append(self, p_object):
        return super(_ListType, self).append(
            self.check_value(p_object)
        )

    def check_value(self, value):
        return value

    def extend(self, iterable):
        return super(_ListType, self).extend(
            (self.check_value(v) for v in iterable)
        )

    def insert(self, index, p_object):
        return super(_ListType, self).insert(
            index, self.check_value(p_object)
        )

    def __add__(self, y):
        raise ConfError("__add__ is not supported.")

    def __iadd__(self, y):
        raise ConfError("__iadd__ is not supported.")

    def __imul__(self, y):
        raise ConfError("__imul__ is not supported.")

    def __mul__(self, n):
        raise ConfError("__mul__ is not supported.")

    def __repr__(self):
        return self.l_delim+"\n  " + ",\n  ".join(
            "%s" % _format_string(v) for v in self
        ) + "\n"+self.r_delim

    def __rmul__(self, n):
        raise ConfError("__rmul__ is not supported.")

    def __setattr__(self, key, value):
        raise ConfError("No attribute setting on Lists and Arrays!")

    def __setitem__(self, i, y):
        return super(_ListType, self).__setitem__(
            i, self.check_value(y)
        )

    def __setslice__(self, i, j, y):
        return super(_ListType, self).__setslice__(
            i, j, (self.check_value(x) for x in y)
        )


class ConfArray(_ListType):
    l_delim = "["
    r_delim = "]"

    def check_value(self, value):
        _check_scalar_value(value)
        if not len(self):
            self.__dict__["typ"] = type(value)
        elif self.typ != type(value):
            raise ConfError(
                "Array must have common type: %s != %s" % (
                self.typ, type(value))
            )
        return value


class ConfList(_ListType):
    l_delim = "("
    r_delim = ")"

    def check_value(self, value):
        return _check_value(value)


class ConfGroup(object):
    def __init__(self, ini_dict=None):
        if type(ini_dict) == dict:
            for k, v in ini_dict.iteritems():
                setattr(self, k, v)

    def __setattr__(self, key, val):
        self.__dict__[key] = _check_value(val)

    def __repr__(self):
        return "{\n  " + "\n  ".join(
            "%s = %s;" % (k, _format_string(v))
            for k, v in self.__dict__.iteritems()
        ) + "\n}"


class Config(ConfGroup):
    def __repr__(self):
        return "\n".join(
            "%s = %s;" % (k, _format_string(v))
            for k, v in self.__dict__.iteritems()
        ).replace("\n  ", "\n")  # fix wrong indentation for grouped types


_scalar_types = str, int, long, float, bool
_all_types = _scalar_types + (ConfGroup, ConfList, ConfArray)


def _check_scalar_value(val):
    if not type(val) in _scalar_types:
        raise ConfError("Type not supported: %s, %s" % (type(val), val))
    return val


def _check_value(val):
    if not type(val) in _all_types:
        raise ConfError("Type not supported: %s, %s" % (type(val), val))
    return val


def _format_string(obj):
    if type(obj) == str:
        return '"%s"' % obj.replace('"', r'\"')
    else:
        return repr(obj).replace("\n", "\n  ")


