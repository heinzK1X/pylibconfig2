pylibconfig2
============

Pure python library for libconfig syntax. IO works via strings only. Thus,
include directives are not supported.


Usage
-----

Scalar types are pythons basic types str, int, long, float, bool. The libconfig
types Array, List, Group are implemented as ConfArray, ConfList, ConfGroup,
respectively. A config is setup from a string only, and represented as a string
automatically.


The config
~~~~~~~~~~

Config represents a libconfig configuration. Access works via attributes.
The string representation is itself a readable as a config:

    >>> import pylibconfig2 as cfg
    >>> c = cfg.Config("my_setting = 5;")
    >>> c.my_setting
    5
    >>> str(c)
    'my_setting = 5;'

These functions are given for convenience:

    keys()
    values()
    items()
    get(key, default)
    set(key, value)


An array
~~~~~~~~

ConfArray represents a libconfig array. Access works via the [] operator:

    >>> import pylibconfig2 as cfg
    >>> c = cfg.Config("my_array = [1, 2, 3];")
    >>> c.my_array[1]
    2


A list
~~~~~~

ConfList represents a libconfig list. Access works via the [] operator:

    >>> import pylibconfig2 as cfg
    >>> c = cfg.Config('my_list = (1.5, 2L, 0xee, "string");')
    >>> c.my_list[1]
    2L


A group
~~~~~~~

ConfGroup represents a libconfig group. Access works via attributes:

    >>> import pylibconfig2 as cfg
    >>> c = cfg.Config("my_group = {my_setting = 5;};")
    >>> c.my_group.my_setting
    5

Again, these functions are given for convenience:

    keys()
    values()
    items()
    get(key, default)
    set(key, value)