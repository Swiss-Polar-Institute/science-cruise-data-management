from django.core.management.base import BaseCommand
from main.models import Sample, Project, SamplingMethod
# import the function from createreports.reportproject.save_into_file - actually probably don't need this becasue I want a list rather than the file

import csv

# add the class command here (look at exportgps tracks command for help)
class Command(BaseCommand):
    help = 'Compare lists of samples'

    def add_arguments(self, parser):
        parser.add_argument('data_file_directory', type=str, help="Type in the name of the directory in which the data file can be found")
        parser.add_argument('data_filename', type=str, help="Type in the name of the data file")
        parser.add_argument('project_number', type=int, help="Project number to analyse samples from")
        parser.add_argument('sampling_method_name', type=str, help="Method by which the samples were collected")

    def handle(self, *args, **options):
        data_file_directory = options['data_file_directory']
        data_filename = options['data_filename']
        project_number = options['project_number']
        sampling_method_name = options['sampling_method_name']

        compareSampleLists = CompareSampleLists.compare_sample_lists(sampling_method_name, project_number, data_file_directory, data_filename)

class CompareSampleLists():
    '''Compares two lists of sample codes, one from the database and one from a set of data, and outputs lists of sample codes that meet certain criteria'''

    @staticmethod
    def create_sample_list_from_database(sampling_method_name, project_number):
        '''This function is very similar and modified from to Command.samples from createreports.py. It gets a list of samples from the database following the criteria in the function set-up'''

        sample_numbers = []

        for sample in Sample.objects.filter(event__sampling_method__name=sampling_method_name).filter(project__number=project_number).order_by('expedition_sample_code'):
            sample_numbers.append(sample.expedition_sample_code)

        return sample_numbers

    @staticmethod
    def get_list_of_data_samples(data_file_directory, data_filename):
        '''This function gets reads sample codes into a list from a csv file containing data'''

        data_filename = "{}/{}".format(data_file_directory, data_filename)

        sample_numbers = []

        # reads in the file and lists the sample codes
        with open(data_filename, 'r') as file:
            reader = csv.reader(file, delimiter=',')

            for row in reader:
                sample_numbers.append(row[0])

            print(sample_numbers)

            return sample_numbers

# Put in here a thing to normalise the sample numbers (with the julian day)
    @staticmethod
    def normalise_expedition_sample_code(sample_numbers):
        '''This function takes an input list of expedition sample codes and normalises the sample codes within it, ensuring each section of the code is in the correct format (in particular the julian day)'''

        normalised_sample_codes = []

        for sample_code in sample_numbers: 

            # splits the input sample code into constituent parts
            ship_string = sample_code.split('/')[0]
            mission_acronym_string = sample_code.split('/')[1]
            leg_string = sample_code.split('/')[2]
            project_number_string = sample_code.split('/')[3]
            julian_day = "{0:03d}".format(int(sample_code.split('/')[4]))
            event_number_string = sample_code.split('/')[5]
            pi_initials_string = sample_code.split('/')[6]
            project_sample_code_string = sample_code.split('/')[7]

            # puts the expedition sample code back together once it has been normalised
            normalised_expedition_sample_code =ship_string + "/" + mission_acronym_string + "/" + leg_string + "/" + project_number_string + "/" + julian_day + "/" + event_number_string + "/" + pi_initials_string + "/" + project_sample_code_string

            # appends the normalised sample codes back to the list
            normalised_sample_codes.append(normalised_expedition_sample_code)

        return sorted(normalised_sample_codes)


    @staticmethod
    def compare_lists(lista, listb):
        '''This function compares two lists and prints these lists according to certain criteria'''
        print("LIST A (TOTAL: ", len(lista), "):", lista)
        print("LIST B (TOTAL: ", len(listb), "):", listb)

        lista_and_listb = []

        for item in lista:
            if item in listb:
                lista_and_listb.append(item)

        print("The following items are in both lists (Total: ", len(lista_and_listb), "):", lista_and_listb)

        lista_not_listb = []

        for item in lista:
            if item not in listb:
                lista_not_listb.append(item)

        print("The following items are the first list but not the second list (Total: ", len(lista_not_listb), "):", lista_not_listb)

        listb_not_lista = []

        for item in listb:
            if item not in lista:
                listb_not_lista.append(item)

        print("The following items are the second list but not the first (Total: ", len(listb_not_lista), "):", listb_not_lista)


    @staticmethod
    def compare_sample_lists(sampling_method_name, project_number, data_file_directory, data_filename):
        '''This function creates a list of samples from the database and compares it to a list of samples from an input file. It outputs lists samples that match and do not match between the two lists'''

        database_sample_list = CompareSampleLists.create_sample_list_from_database(sampling_method_name, project_number)

        file_sample_list = CompareSampleLists.get_list_of_data_samples(data_file_directory, data_filename)

        normalised_database_sample_list = CompareSampleLists.normalise_expedition_sample_code(database_sample_list)
        print("NORMALISED SAMPLE LIST FROM DATABASE (total:", len(normalised_database_sample_list), "):", normalised_database_sample_list)

        normalised_file_sample_list = CompareSampleLists.normalise_expedition_sample_code(file_sample_list)
        print("NORMALISED SAMPLE LIST FROM FILE (total:", len(normalised_file_sample_list), "):", normalised_file_sample_list)

        CompareSampleLists.compare_lists(normalised_database_sample_list, normalised_file_sample_list)

