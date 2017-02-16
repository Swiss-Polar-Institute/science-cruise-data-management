from django.core.management.base import BaseCommand, CommandError
from data_storage_management.models import Directory
from lxml import etree

class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        metadata_generator = MetadataGenerator()
        metadata_generator.create_all_records()

class MetadataGenerator:
    def __init__(self):
        print("metadata generator created")
        # TODO
        pass

    def create_all_records(self):
        # TODO
        pass

    def create_record(self, output_file, information):
        print(information)
        print("create all records")
        nsmap = {None : "http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/",
                 "xsi": "http://www.w3.org/2001/XMLSchema-instance",
                 "schemaLocation": "http://gcmd.nasa.gov/Aboutus/xml/dif/dif_v9.7.1.xsd"
                 }
        root = etree.Element("DIF", nsmap=nsmap)

        entry_id = etree.SubElement(root, "Entry_ID")
        entry_id.text = "f7947381-6fd7-466f-8894-25d3262cbcf5"
        root.append(entry_id)

        entry_title = etree.SubElement(root, "Entry_Title")
        entry_title.text = "Rock outcrop map of the Antarctic continent derived from Landsat 8 imagery"
        root.append(entry_title)

        entry_summary = etree.SubElement(root, "Summary")
        entry_summary.text="""Test
Hello
<test>

Test
        """
        root.append(entry_summary)


        temporal_coverage = etree.SubElement(root, "Temporal_Coverage")
        start_date = etree.SubElement(temporal_coverage, "Start_Date")
        start_date.text = "2016-07-27"
        temporal_coverage.append(start_date)

        end_date = etree.SubElement(temporal_coverage, "End_Date")
        end_date.text = "2016-07-27"
        temporal_coverage.append(end_date)

        root.append(temporal_coverage)

        b = etree.tostring(root, pretty_print=True)
        print(b.decode('utf-8'))
