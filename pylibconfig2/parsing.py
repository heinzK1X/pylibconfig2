"""
Parsing module of pylibconfig2.
Knowledge on pyparsing and libconfig required =)
"""

from pyparsing import alphas, alphanums, cppStyleComment, Combine, Group, \
    Forward, hexnums, ParseException, ParseFatalException, pythonStyleComment, \
    oneOf, OneOrMore, Optional, QuotedString, Suppress, Word, ZeroOrMore, \
    stringStart, stringEnd
from pylibconfig2.conf_types import ConfArray, ConfError, ConfGroup, ConfList
from ast import literal_eval

assign = Suppress(oneOf(": ="))
delim = Suppress(Optional(";"))
lpar, rpar, lbrk, rbrk, lbrc, rbrc, comma = list(map(Suppress, "()[]{},"))

name = Word(alphas+"*", alphanums+"-_*")("name")
value = Forward()
setting = Forward()


def convert_bool(tokens):
    t = tokens[0].lower()
    vals = {"true": True, "false": False}
    if not t in vals:
        raise ParseFatalException("bool incorrect: %s" % tokens[0])
    else:
        return vals[t]


def convert_num(tokens):
    try:
        res = literal_eval(tokens[0])
    except (SyntaxError, ValueError):
        raise ParseFatalException("Number incorrect: %s" % tokens[0])
    return res


class ListGroup(Group):
    """Converts Group from list to ConfList type."""
    def postParse(self, instring, loc, tokenlist ):
        try:
            return [ConfList(tokenlist.asList())]
        except ConfError as e:
            raise ParseFatalException(e.args[0])


class ArrayGroup(Group):
    """Converts Group from list to ConfArray type."""
    def postParse(self, instring, loc, tokenlist ):
        try:
            return [ConfArray(tokenlist.asList())]
        except ConfError as e:
            raise ParseFatalException(e.args[0])


def convert_group(tokens):
    """Converts parseResult from to ConfGroup type."""
    tok = tokens.asList()
    dic = dict(tok)
    if not (len(dic) == len(tok)):
        raise ParseFatalException("Names in group must be unique: %s" % tokens)
    return ConfGroup(dic)

# scalar values
val_bool = Word("TRUEFALStruefals")\
    .setParseAction(convert_bool)
val_str = OneOrMore(QuotedString('"', escChar='\\'))\
    .setParseAction(lambda t: "".join(t))
val_num = Combine(
    Optional(oneOf("+ -")) + Optional("0x") + Word(hexnums + ".eEL" + "+-") )\
    .setParseAction(convert_num)
val_scalar = val_bool | (val_str | val_num)

# container values
val_array = ArrayGroup(
    lbrk
    + Optional(val_scalar+ZeroOrMore(comma+val_scalar))
    + rbrk
)
val_list = ListGroup(
    lpar
    + Optional(value+ZeroOrMore(comma+value))
    + rpar
)
val_group = (
    lbrc
    + ZeroOrMore(setting).setParseAction(convert_group)
    + rbrc
)

value << (val_group | val_list | val_array | val_scalar)("value")
setting << Group(name + assign + value + delim)
config = (stringStart + ZeroOrMore(setting) + stringEnd)\
    .ignore(cppStyleComment)\
    .ignore(pythonStyleComment)\
    .setParseAction(convert_group)

