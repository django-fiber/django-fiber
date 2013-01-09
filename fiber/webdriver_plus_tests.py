"""
Selenium / Webdriver plus tests.

These tests will fire up your default browser and do some tests against a host and optionally
a port provided by you.

Webdriverplus must be installed: pip install https://github.com/tomchristie/webdriverplus/zipball/master - supports the `wait` command.

"""

import unittest
import webdriverplus

from selenium.common.exceptions import TimeoutException

HOST = None
PORT = None


class FIberTests(unittest.TestCase):
    def setUp(self):
        super(FIberTests, self).setUp()
        self.driver = webdriverplus.WebDriver(wait=10, reuse_browser=False)

    def tearDown(self):
        self.driver.quit()


class LoginTests(FIberTests):

    def setUp(self):
        super(LoginTests, self).setUp()
        self.driver.get('http://%s:%s/@fiber' % (HOST, PORT))

    def test_login_succeeds(self):
        """
        Try to login with admin / admin.
        """
        elem = self.driver.find('input', id='id_username')
        elem.send_keys('admin')
        elem = self.driver.find('input', id='id_password')
        elem.send_keys('admin')
        elem = self.driver.find(id='login_button')
        elem.click()
        self.assertRaises(TimeoutException, self.driver.find, '.errornote')  # Not found

    def test_login_fails(self):
        """
        If login fails, an element will be appended to the form of class `.errornote`
        """
        elem = self.driver.find('input', id='id_username')
        elem.send_keys('invalidname')
        elem = self.driver.find('input', id='id_password')
        elem.send_keys('invalidpassword')
        elem = self.driver.find(id='login_button')
        elem.click()
        node = self.driver.find('.errornote')
        self.assertTrue(node)


if __name__ == '__main__':

    def usage():
        return 'Usage: %s hostname port' % __file__

    import sys
    assert(len(sys.argv) >= 3), usage()
    try:
        HOST = sys.argv[1]
        sys.argv.pop(1)
    except IndexError:
        print usage()
        sys.exit(2)
    try:
        PORT = sys.argv[1]
        sys.argv.pop(1)
    except IndexError:
        print usage()
        sys.exit(2)

    unittest.main()
