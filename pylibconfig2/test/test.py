import doctest
import unittest
import sys

import pylibconfig2 as cfg
from pylibconfig2 import conf_types

################################################################ io strings ###
bad_inp_0 = """
x
"""
bad_inp_1 = """
foo:
{
  a = 100;
  b = 10;
  a = "hello";
};
"""

inp_0 = ""
outp_0 = ""

inp_1 = """
// Empty file

// (no settings, only comments)
"""
outp_1 = ""

inp_2 = """

// File with extraneous whitespace.

    foo = 1;
toto = true;


	bar
	=
	  "Hello, "
	"world!"
;


baz = 2;




"""
outp_2 = """
foo = 1;
bar = "Hello, world!";
baz = 2;
toto= true;
"""

inp_3 = """
// File has no trailing newline.

foo = 1;

bar = 2;

baz = 3;"""
outp_3 = """
foo = 1;
bar = 2;
baz = 3;
"""

inp_4 = """
// Last line has whitespace but no trailing newline.

foo = 1;
toto= false;

bar = 2;

			"""
outp_4 = """
foo = 1;
bar = 2;
toto = false;
"""


################################################################### testing ###
class Test(unittest.TestCase):
    def test_bad_input_0(self):
        self.assertRaises(
            cfg.ParseException,
            cfg.Config,
            bad_inp_0
        )

    def test_bad_input_1(self):
        self.assertRaises(
            cfg.ParseFatalException,
            cfg.Config,
            bad_inp_1
        )

    def test_input_0(self):
        self.assertEqual(
            str(cfg.Config(inp_0)),
            outp_0
        )

    def test_input_1(self):
        self.assertDictEqual(
            cfg.Config(inp_1).__dict__,
            cfg.Config(outp_1).__dict__
        )

    def test_input_2(self):
        self.assertDictEqual(
            cfg.Config(inp_2).__dict__,
            cfg.Config(outp_2).__dict__
        )

    def test_input_3(self):
        self.assertDictEqual(
            cfg.Config(inp_3).__dict__,
            cfg.Config(outp_3).__dict__
        )

    def test_input_4(self):
        self.assertDictEqual(
            cfg.Config(inp_4).__dict__,
            cfg.Config(outp_4).__dict__
        )

suite = unittest.TestSuite((
    unittest.TestLoader().loadTestsFromTestCase(Test),
    doctest.DocTestSuite(conf_types),
))


if __name__ == '__main__':
    res = unittest.TextTestRunner(
        verbosity=2
    ).run(suite)
    if res.failures:
        sys.exit(-1)



