import unittest
import re

class InputValidator:
    def validate_ip_port(hostname, with_port=True):
        if with_port:
            return re.search('^\d+\.\d+\.\d+\.\d+:\d+$', hostname)
        else:
            return re.search('^\d+\.\d+\.\d+\.\d+$', hostname)

    def validate_device_id(device_id):
        return re.search('^[a-zA-Z0-9]+$', device_id) or InputValidator.validate_ip_port(device_id, with_port=True)
    
    def validate_app_identifier(app_id):
        return re.search('^([A-Za-z]{1}[A-Za-z\d_]*\.)+[A-Za-z][A-Za-z\d_]*$', app_id)

    def validate_version_number(version):
        return re.search('^\d+(?:\.\d+)*$', version)


class TestValidatorMethods(unittest.TestCase):
    def test_ip_with_port(self):
        self.assertTrue(InputValidator.validate_ip_port('192.168.1.249:80', with_port=True))
        self.assertFalse(InputValidator.validate_ip_port('192.168.1.249', with_port=True))
        self.assertFalse(InputValidator.validate_ip_port(' 192.168.1.249   ', with_port=True))
        self.assertFalse(InputValidator.validate_ip_port('N0t.aN.1p.555', with_port=True))

    def test_ip_without_port(self):
        self.assertFalse(InputValidator.validate_ip_port('192.168.1.249:80', with_port=False))
        self.assertTrue(InputValidator.validate_ip_port('192.168.1.249', with_port=False))

    def test_device_id(self):
        self.assertTrue(InputValidator.validate_device_id('K6T6R17909001485'))
        self.assertTrue(InputValidator.validate_device_id('0000000000000000'))
        self.assertTrue(InputValidator.validate_device_id('192.168.1.41:5555'))
        self.assertFalse(InputValidator.validate_device_id('192.168.1.41:5555 & cat /etc/passwd'))
        self.assertFalse(InputValidator.validate_device_id(' & ls'))

    def test_app_identifier(self):
        self.assertTrue(InputValidator.validate_app_identifier('com.ookbee.ookbeecomics.android'))
        self.assertTrue(InputValidator.validate_app_identifier('com.mojang.minecraftpe'))
        self.assertFalse(InputValidator.validate_app_identifier('com.mojang.minecraftpe && rm -rf'))
        self.assertFalse(InputValidator.validate_app_identifier('comookbeeookbeecomicsandroid'))

    def test_version_number(self):
        self.assertTrue(InputValidator.validate_version_number('7.0'))
        self.assertTrue(InputValidator.validate_version_number('8.0.1'))
        self.assertTrue(InputValidator.validate_version_number('10'))
        self.assertFalse(InputValidator.validate_version_number('9.'))
        self.assertFalse(InputValidator.validate_version_number('.0'))
        self.assertFalse(InputValidator.validate_version_number('7.0 & pwd'))


if __name__ == '__main__':
    unittest.main()
