from django.core.management.base import BaseCommand, CommandError
from metadata.models import MetadataEntry
from lxml import etree

class Command(BaseCommand):
    help = 'Generate metadata file'

    def add_arguments(self, parser):
        parser.add_argument('metadata_id', type=str)

    def handle(self, *args, **options):
        export_metadata_file = ExportMetadataFile(options['metadata_id'])
        export_metadata_file.do()

class ExportMetadataFile:
    def __init__(self, metadata_id):
        self.metadata_id = int(metadata_id)
        self.metadata_entry = MetadataEntry.objects.get(id=self.metadata_id)
        self.xml_root = None

    def add_char_element(self, tag, field):
        element = etree.SubElement(self.xml_root, tag)
        element.text = getattr(self.metadata_entry, field)
        self.xml_root.append(element)

    def do(self):
        fp = open("/tmp/test_dif.xml", "wb")

        nsmap = {None: "http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/",
                 "xsi": "http://www.w3.org/2001/XMLSchema-instance",
                 "schemaLocation": "http://gcmd.nasa.gov/Aboutus/xml/dif/dif_v9.7.1.xsd"
                 }
        self.xml_root = etree.Element("DIF", nsmap=nsmap)

        self.add_char_element('Entry_ID', 'entry_id')
        self.add_char_element('Entry_Title', 'entry_title')
        self.add_char_element('Quality', 'quality')
        self.add_char_element('Access_Constraints', 'access_constraints')
        self.add_char_element('Use_Constraints', 'use_constraints')
        self.add_char_element('Data_Set_Language', 'data_set_language')
        self.add_char_element('Originating_Center', 'originating_center')
        self.add_char_element('Parent_DIF', 'parent_dif')
        self.add_char_element('Metadata_Name', 'metadata_name')
        self.add_char_element('Metadata_Version', 'metadata_version')
        self.add_char_element('Dif_Revision_History', 'dif_revision_history')

        b = etree.tostring(self.xml_root, pretty_print=True)
        print(b.decode('utf-8'))
        fp.write(b)
        fp.close()


        # entry_id = etree.SubElement(root, "Entry_ID")
        # entry_id.text = metadata_entry.entry_id
        # root.append(entry_id)
        #
        # # entry_title = etree.SubElement(root, "Entry_Title")
        # # entry_title.text = "Rock outcrop map of the Antarctic continent derived from Landsat 8 imagery"
        # # root.append(entry_title)
        # #
        # # entry_summary = etree.SubElement(root, "Summary")
        # # entry_summary.text = """Test
        # # Hello
        # # <test>
        # #
        # # Test
        # #         """
        # # root.append(entry_summary)
        # #
        # # temporal_coverage = etree.SubElement(root, "Temporal_Coverage")
        # # start_date = etree.SubElement(temporal_coverage, "Start_Date")
        # # start_date.text = "2016-07-27"
        # # temporal_coverage.append(start_date)
        # #
        # # end_date = etree.SubElement(temporal_coverage, "End_Date")
        # # end_date.text = "2016-07-27"
        # # temporal_coverage.append(end_date)
        # #
        # # root.append(temporal_coverage)
        #
        # b = etree.tostring(root, pretty_print=True)
        # fp.write(b)
        # fp.close()

