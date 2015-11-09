import doctest
import unittest
import sys
import tempfile

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

intp_5 = """
foo = 1;
toto = false;
"""
outp_5 = """
bar = 2;
titi = true;
foo = 1;
toto = false;
"""

intp_6 = """
bar = 2;
titi = true;
"""
outp_6 = """
foo = 1;
toto = false;
bar = 2;
titi = true;
"""

inp_7 = """
// bool test

my_group =
{
    bool_false = false
    bool_true = true
}
"""

inp_8 = """
// testing separators in groups

my_group = {val1 = "semicolon"; val2 = "comma", val3 = "nothing" val4 = "end"}
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

    def test_input_8(self):
        cfg.Config(inp_8)

    def test_empty(self):
        self.assertDictEqual(
            cfg.Config('').__dict__,
            cfg.Config().__dict__
        )
        
    def test_read_string(self):
        cfg1 = cfg.Config(inp_4)
        cfg2 = cfg.Config()
        cfg2.read_string(outp_4)
        self.assertDictEqual(
            cfg1.__dict__,
            cfg2.__dict__
        )

    def test_read_file_simple_no_include(self):
        temp = tempfile.NamedTemporaryFile()
        try:
            cfg1 = cfg.Config(inp_4)
            temp.write(outp_4.encode("UTF-8"))
            temp.flush()
            cfg2 = cfg.Config()
            cfg2.read_file(temp.name)
            self.assertDictEqual(
                cfg1.__dict__,
                cfg2.__dict__
            )
        finally:
            temp.close()

    def test_read_file_include(self):
        temp1 = tempfile.NamedTemporaryFile()
        temp2 = tempfile.NamedTemporaryFile()
        inc1 = '@include "' + temp2.name + '"'
        try:
            cfg1 = cfg.Config(outp_5)
            temp1.write(inc1.encode("UTF-8"))
            temp1.write(intp_5.encode("UTF-8"))
            temp1.flush()
            temp2.write(intp_6.encode("UTF-8"))
            temp2.flush()
            cfg2 = cfg.Config()
            cfg2.read_file(temp1.name)
            cfg3 = cfg.Config(outp_6)
            self.assertDictEqual(
                cfg1.__dict__,
                cfg2.__dict__
            )
            self.assertDictEqual(
                cfg3.__dict__,
                cfg2.__dict__
            )
        finally:
            temp1.close()
            temp2.close()
            
    def test_expand_include_with_bad_recursion(self):
        temp1 = tempfile.NamedTemporaryFile()
        temp2 = tempfile.NamedTemporaryFile()
        inc2 = '@include "' + temp2.name + '"'
        inc3 = '@include "' + temp1.name + '"'
        try:
            temp1.write(inc2.encode("UTF-8")) 
            temp1.write(intp_5.encode("UTF-8"))
            temp1.flush()
            temp2.write(inc3.encode("UTF-8"))
            temp2.write(intp_6.encode("UTF-8"))
            temp2.flush()
            string1 = cfg.Config.expand_include(temp1.name)
            string2 = cfg.Config.expand_include(temp2.name)
            self.assertEqual(string1, None)
            self.assertEqual(string2, None)
        finally:
            temp1.close()
            temp2.close()

    def test_bool_lookup(self):
        c = cfg.Config(inp_7)
        self.assertEqual(c.my_group.bool_true, True)
        self.assertEqual(c.my_group.bool_false, False)
        self.assertEqual(c.lookup('my_group.bool_true'), True)
        self.assertEqual(c.lookup('my_group.bool_false'), False)


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



