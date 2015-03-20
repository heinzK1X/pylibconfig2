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

intp_6 = """
bar = 2;
titi = true;
"""

outp_5 = """
bar = 2;
titi = true;
foo = 1;
toto = false;
"""

outp_6 = """
foo = 1;
toto = false;
bar = 2;
titi = true;
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
    
    def test_empty(self):
        self.assertDictEqual(
            cfg.Config('').__dict__,
            cfg.Config().__dict__
        )
        
    def test_readString(self):
        cfg1 = cfg.Config(inp_4)
        cfg2 = cfg.Config()
        cfg2.readString(outp_4)
        self.assertDictEqual(
            cfg1.__dict__,
            cfg2.__dict__
        )
        
    
    def test_readFile_simple_no_include(self):
        temp = tempfile.NamedTemporaryFile()
        try:
            cfg1 = cfg.Config(inp_4)
            temp.write(outp_4)
            temp.flush();
            cfg2 = cfg.Config()
            cfg2.readFile(temp.name)
            self.assertDictEqual(
                cfg1.__dict__,
                cfg2.__dict__
            )
        finally:
            temp.close()

    def test_readFile_include(self):
        temp1 = tempfile.NamedTemporaryFile()
        temp2 = tempfile.NamedTemporaryFile()
        try:
            cfg1 = cfg.Config(outp_5)
            temp1.write('@include "' + temp2.name + '"')
            temp1.write(intp_5)
            temp1.flush();
            temp2.write(intp_6)
            temp2.flush()
            cfg2 = cfg.Config()
            cfg2.readFile(temp1.name)
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
        try:
            temp1.write('@include "' + temp2.name + '"')
            temp1.write(intp_5)
            temp1.flush();
            temp2.write('@include "' + temp1.name + '"')
            temp2.write(intp_6)
            temp2.flush()
            string1 = cfg.Config.expand_include(temp1.name)
            string2 = cfg.Config.expand_include(temp2.name)
            self.assertEqual(string1, None)
            self.assertEqual(string2, None)
        finally:
            temp1.close()
            temp2.close()

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



