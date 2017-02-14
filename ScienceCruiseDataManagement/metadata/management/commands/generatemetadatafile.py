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

    def add_char_element(self, parent, tag, text):
        if text != "" and text is not None:
            element = etree.SubElement(parent, tag)
            element.text = text

    def add_date_element(self, parent, tag, date):
        if date is not None:
            element = etree.SubElement(parent, tag)
            element.text = date.strftime("%F")

    def add_data_set_citation(self, parent, tag, data_set_citations):
        for data_set_citation in data_set_citations.all():
            data_set_citation_xml = etree.SubElement(parent, tag)

            self.add_char_element(data_set_citation_xml, "Dataset_Creator",
                                  "{} {}".format(data_set_citation.dataset_creator.name_first, data_set_citation.dataset_creator.name_last))
            self.add_char_element(data_set_citation_xml, "Dataset_Title", data_set_citation.dataset_title)
            self.add_date_element(data_set_citation_xml, "Dataset_Release_Date", data_set_citation.dataset_release_date)
            self.add_char_element(data_set_citation_xml, "Dataset_Publisher", data_set_citation.dataset_publisher)
            self.add_char_element(data_set_citation_xml, "Version", data_set_citation.version)
            self.add_char_element(data_set_citation_xml, "Other_Citation_Details", data_set_citation.other_citation_details)

    def add_sensor_names(self, parent, tag, sensor_names):
        for sensor_name in sensor_names.all():
            print(sensor_name.uuid)
            sensor_name_xml = etree.SubElement(parent, tag, {'uuid': sensor_name.uuid})
            self.add_char_element(sensor_name_xml, 'Short_Name', sensor_name.short_name)
            self.add_char_element(sensor_name_xml, 'Long_Name', sensor_name.long_name)

    def do(self):
        fp = open("/tmp/test_dif.xml", "wb")

        nsmap = {None: "http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/",
                 "xsi": "http://www.w3.org/2001/XMLSchema-instance",
                 "schemaLocation": "http://gcmd.nasa.gov/Aboutus/xml/dif/dif_v9.7.1.xsd"
                 }
        xml_root = etree.Element("DIF", nsmap=nsmap)

        self.add_char_element(xml_root, 'Entry_ID', self.metadata_entry.entry_id)
        self.add_char_element(xml_root, 'Entry_Title', self.metadata_entry.entry_title)
        self.add_char_element(xml_root, 'Quality', self.metadata_entry.quality)
        self.add_char_element(xml_root, 'Access_Constraints', self.metadata_entry.access_constraints)
        self.add_char_element(xml_root, 'Use_Constraints', self.metadata_entry.use_constraints)
        self.add_char_element(xml_root, 'Data_Set_Language', self.metadata_entry.data_set_language)
        self.add_char_element(xml_root, 'Originating_Center', self.metadata_entry.originating_center)
        self.add_char_element(xml_root, 'Parent_DIF', self.metadata_entry.parent_dif)
        self.add_char_element(xml_root, 'Metadata_Name', self.metadata_entry.metadata_name)
        self.add_char_element(xml_root, 'Metadata_Version', self.metadata_entry.metadata_version)
        self.add_char_element(xml_root, 'Dif_Revision_History', self.metadata_entry.dif_revision_history)
        self.add_data_set_citation(xml_root, 'Data_Set_Citation', self.metadata_entry.data_set_citation)
        self.add_sensor_names(xml_root, 'Sensor_Name', self.metadata_entry.sensor_name)

        b = etree.tostring(xml_root, pretty_print=True)
        print(b.decode('utf-8'))
        fp.write(b)
        fp.close()