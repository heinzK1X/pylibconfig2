"""
The types of libconfig.

Scalar python types are used. The libconfig types Array, List, Group are
 implemented as ConfArray, ConfList, ConfGroup, respectively.
ConfArray and ConfList extend the python list type. ConfGroup uses __dict__ as
 its data storage.
"""
import pyparsing as pp
import sys
if sys.version > '3':
    long = int


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
        if type(k) == int and k >= 0 and k < len(self):
            val = self[k]
            if not len(keys):
                return val
            if isinstance(val, (_ListType, ConfGroup)):
                return val._lookup(keys)
                
    def _setup(self, keys, value):
        k = self.array_index.parseString(keys.pop(0))[0]
        if type(k) == int and k >= 0 and k < len(self):
            if not len(keys):
                self[k] = self.check_value(value)
                return True
            elif isinstance(self[k], (_ListType, ConfGroup)):
                return self[k]._setup(keys, value)
        return False

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
        return list(self.__dict__.keys())

    def values(self):
        return list(self.__dict__.values())

    def items(self):
        return list(self.__dict__.items())

    def _lookup(self, keys):
        k = keys.pop(0)
        if k in self.__dict__:
            val = self.__dict__[k]
            if not len(keys):
                return val
            if isinstance(val, (_ListType, ConfGroup)):
                return val._lookup(keys)
                
    def _setup(self, keys, value):
        k = keys.pop(0)
        if not len(keys):
            self.__dict__[k] = value
            return True
        elif isinstance(self.__dict__.get(k), (_ListType, ConfGroup)):
            return self.__dict__[k]._setup(keys, value)
        return False

    def __init__(self, ini_dict=None):
        if type(ini_dict) == dict:
            for k, v in ini_dict.items():
                setattr(self, k, v)

    def __setattr__(self, key, val):
        self.__dict__[_check_name(key)] = _check_value(val)

    def __repr__(self):
        return "{\n  " + "\n  ".join(
            "%s = %s;" % (k, _format_string(v))
            for k, v in self.__dict__.items()
        ) + "\n}"

_scalar_types = str, int, long, float, bool
_all_types = _scalar_types + (ConfGroup, ConfList, ConfArray)


def _check_scalar_value(val):
    if not type(val) in _scalar_types:
        raise ConfError("Type not supported: %s, %s, allowed types: %s"
                        % (type(val), val, _scalar_types))
    return val


def _check_value(val):
    if not type(val) in _all_types:
        raise ConfError("Type not supported: %s, %s, allowed types: %s"
                        % (type(val), val, _all_types))
    return val


def _check_name(key):
    try:
        parsing.name.parseString(key)
    except parsing.ParseException:
        raise ConfError("Name not valid: %s" % key)
    return key


def _format_string(obj):
    if type(obj) == str:
        return '"%s"' % obj.replace('"', r'\"')
    else:
        return repr(obj).replace("\n", "\n  ")


from pylibconfig2 import parsing
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

    Setting values should be done by path:
    >>> c = Config('')
    >>> c.setup('foo', 1)
    True
    >>> c.setup('bar', '{hello = "world"}')
    True
    >>> c.lookup('bar.hello')
    'world'
    >>> c.setup('a.nonexisting.group', '"returns False!"')
    False

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
        
    def setup(self, key, value):
        value = parsing.value.parseString(str(value))[0]
        return self._setup(key.split('.'), value)

    @staticmethod
    def expand_include(filename):
        """
        Expand the content of a file into a string.

        If @include directives are found in the config, they are expanded by
        this function. In case recursion is detected or a RunTimeError is
        thrown, ``None`` is returned.
        """
        def _expand_include_rec(filename):
            for line in open(filename):
                line_stripped = line.strip().replace("//", "#")
                if line_stripped.startswith('@include '):
                    include_to_clean = line_stripped.split(None, 1)[1]
                    include_filename = include_to_clean.replace('"'," ").strip()
                    for included_line in _expand_include_rec(include_filename):
                        yield included_line
                else:
                    yield line
        try:
            lines = []
            for line in _expand_include_rec(filename):
                lines.append(line)
            return ''.join(lines)
        except RuntimeError:
            return None

    def read_string(self, string):
        self.__init__(string)
        
    def read_file(self, filename):
        string = Config.expand_include(filename)
        if string is None:
            raise ConfError(
                "Recursion of @include detected"
            )
        self.read_string(string)

    def __init__(self, string=''):
        res = parsing.config.parseString(string)[0]
        super(Config, self).__init__(res.__dict__)

    def __repr__(self):
        return "\n".join(
            "%s = %s;" % (k, _format_string(v))
            for k, v in self.__dict__.items()
        ).replace("\n  ", "\n")  # fix wrong indentation for grouped types
