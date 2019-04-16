from django.test import SimpleTestCase

import main.utils_coordinates

class UtilsCoordinates(SimpleTestCase):
    def setUp(self):
        pass

    def test_utils_coordinates_process(self):
        template_information = {}

        main.utils_coordinates.process("test01\ntest02", template_information)

        self.assertEqual(template_information["list_of_coordinates"], [])
