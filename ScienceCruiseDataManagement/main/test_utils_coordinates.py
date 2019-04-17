from django.test import SimpleTestCase

import main.utils_coordinates


class UtilsCoordinates(SimpleTestCase):
    def setUp(self):
        pass

    def test_utils_coordinates_process_invalid_coordinates(self):
        template_information = {}

        main.utils_coordinates.process("test01\ntest02", template_information)

        self.assertEqual(template_information["list_of_coordinates"], [])
        self.assertTrue("error" in template_information)
        self.assertTrue("Aborts" in template_information["error"])

    def test_utils_coordinates(self):
        template_information = {}

        main.utils_coordinates.process("41 23 00.00 N 2 200 00.00 E", template_information)
        self.assertDictEqual(template_information,
                             {'output_format_name2': 'Degrees and decimal minutes',
                              'input_format_name': 'Degrees, minutes and decimal seconds',
                              'list_of_coordinates':
                                  [{'input': '41 23 00.00 N 2 200 00.00 E',
                                    'output2': '41 23.000 N 5 20.000 E',
                                    'output1': '41.383 5.333'}],
                              'output_format_name1': 'Decimal degrees'})


        template_information = {}
        main.utils_coordinates.process("""41 23 00.00 N 2 200 00.00 E
51 30 26.00 N 0 7 39.00 W""", template_information)

        self.assertDictEqual(template_information,
                             {'list_of_coordinates': [
                                 {'input': '41 23 00.00 N 2 200 00.00 E', 'output1': '41.383 5.333',
                                  'output2': '41 23.000 N 5 20.000 E'},
                                 {'input': '51 30 26.00 N 0 7 39.00 W', 'output1': '51.507 -0.128',
                                  'output2': '51 30.433 N 0 7.650 W'}], 'output_format_name1': 'Decimal degrees',
                              'input_format_name': 'Degrees, minutes and decimal seconds',
                              'output_format_name2': 'Degrees and decimal minutes'}
                             )