"""
Selenium / Webdriver plus tests. 

These tests will fire up your default browser and do some tests against a host and optionally
a port provided by you.

Webdriverplus must be installed: pip install webdriverplus

"""

import unittest

import webdriverplus

HOST = None
PORT = '8000'

class FIberTests(unittest.TestCase):
    def setUp(self):
        super(FIberTests, self).setUp()
        self.driver = webdriverplus.WebDriver(reuse_browser=True)

    def tearDown(self):
        #self.driver.quit()
        pass

class LoginTests(FIberTests):
    def setUp(self):
        super(LoginTests, self).setUp()
        self.driver.get('http://%s:%s/@fiber' % (HOST, PORT))

    def test_login_succeeds(self):
        elem = self.driver.find('input', id='id_username')
        elem.send_keys('admin')
        elem = self.driver.find('input', id='id_password')
        elem.send_keys('admin')
        elem = self.driver.find(id='login_button')
        elem.click()
        node = self.driver.find('.errornote')
        self.assertFalse(node)


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
    import sys
    try: 
        HOST = sys.argv[1]
        sys.argv.pop(1)
    except IndexError:
        print 'Usage: %s hostname [port]' % __file__
        sys.exit(2)
    try:
        PORT = sys.argv[1]
        sys.argv.pop(1)
    except IndexError:
        pass
    
    unittest.main()
