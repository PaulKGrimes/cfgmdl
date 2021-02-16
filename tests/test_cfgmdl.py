"""
Example unit tests for cfgmdl package
"""
import unittest
import cfgmdl

class ExampleTestCase(unittest.TestCase):
    def setUp(self):
        self.message = 'Hello, world'

    def tearDown(self):
        pass

    def test_run(self):
        foo = cfgmdl.Example(self.message)
        self.assertEqual(foo.run(), self.message)

    def test_failure(self):
        self.assertRaises(AttributeError, cfgmdl.cfgmdl)
        foo = cfgmdl.Example(self.message)
        self.assertRaises(RuntimeError, foo.run, True)

if __name__ == '__main__':
    unittest.main()
