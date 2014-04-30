"""
The types of libconfig.

Scalar python types are used. The libconfig types Array, List, Group are
 implemented as ConfArray, ConfList, ConfGroup, respectively.
ConfArray and ConfList extend the python list type. ConfGroup uses __dict__ as
 its data storage.
"""
import pyparsing as pp

class ConfError(Exception):
    pass

class _ListType(list):
    l_delim = ""
    r_delim = ""
    array_index = (
        pp.Suppress("[") + pp.Word(pp.nums) + pp.Suppress("]")
    ).setParseAction(lambda t: int(t[0]))

    def __init__(self, ini_list=None):
        super(_ListType, self).__init__()
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

    def _lookup(self, keys):
        k = self.array_index.parseString(keys.pop(0))[0]
        if k and k < len(self):
            val = self[k]
            if not len(keys):
                return val
            if isinstance(val, (_ListType, ConfGroup)):
                return val._lookup(keys)

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
    """
    ConfArray represents a libconfig array.

    Access works via the [] operator:
    >>> c = Config("my_array = [1, 2, 3];")
    >>> c.my_array[1]
    2
    """
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
    """
    ConfList represents a libconfig list.

    Access works via the [] operator:
    >>> c = Config('my_list = (1.5, 2L, 0xee, "string");')
    >>> c.my_list[1]
    2L
    """
    l_delim = "("
    r_delim = ")"

    def check_value(self, value):
        return _check_value(value)


class ConfGroup(object):
    """
    ConfGroup represents a libconfig group.

    Access works via attributes:
    >>> c = Config("my_group = {my_setting = 5;};")
    >>> c.my_group.my_setting
    5

    These functions are forwarded for convenience:

        keys()
        values()
        items()
        get(key, default)
        set(key, value)
    """

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def set(self, key, value):
        return setattr(self, key, value)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def _lookup(self, keys):
        k = keys.pop(0)
        if k in self.__dict__:
            val = self.__dict__[k]
            if not len(keys):
                return val
            if isinstance(val, (_ListType, ConfGroup)):
                return val._lookup(keys)

    def __init__(self, ini_dict=None):
        if type(ini_dict) == dict:
            for k, v in ini_dict.iteritems():
                setattr(self, k, v)

    def __setattr__(self, key, val):
        self.__dict__[_check_name(key)] = _check_value(val)

    def __repr__(self):
        return "{\n  " + "\n  ".join(
            "%s = %s;" % (k, _format_string(v))
            for k, v in self.__dict__.iteritems()
        ) + "\n}"


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


from parsing import ParseException, name
def _check_name(key):
    try:
        name.parseString(key)
    except ParseException:
        raise ConfError("Name not valid: %s" % key)
    return key


def _format_string(obj):
    if type(obj) == str:
        return '"%s"' % obj.replace('"', r'\"')
    else:
        return repr(obj).replace("\n", "\n  ")


from parsing import config
class Config(ConfGroup):
    """
    Config represents a libconfig configuration.

    Access works via attributes:
    >>> c = Config("my_setting = 5;")
    >>> c.my_setting
    5

    Or via lookup as in the original libconfig way (no exceptions..):
    >>> c = Config('my = {nested = {sett = (0, {ng = "rocks!"})}}')
    >>> c.lookup('my.nested.foo')
    >>> c.lookup('my.nested.sett.[42]')
    >>> c.lookup('my.nested.sett.[1].ng')
    'rocks!'
    >>> c.lookup('my.nested.foo', 'bar')
    'bar'

    These functions are forwarded for convenience:

        keys()
        values()
        items()
        get(key, default)
        set(key, value)
    """
    def lookup(self, key, default=None):
        res = self._lookup(key.split('.'))
        return res if res else default

    def __init__(self, string):
        res = config.parseString(string)[0]
        super(Config, self).__init__(res.__dict__)

    def __repr__(self):
        return "\n".join(
            "%s = %s;" % (k, _format_string(v))
            for k, v in self.__dict__.iteritems()
        ).replace("\n  ", "\n")  # fix wrong indentation for grouped types
