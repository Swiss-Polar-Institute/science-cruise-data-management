from django.core.management.base import BaseCommand, CommandError
from metadata.models import MetadataEntry
from lxml import etree

class Command(BaseCommand):
    help = 'Generate metadata records'

    def add_arguments(self, parser):
        parser.add_argument('metadata_id', type=str)

    def handle(self, *args, **options):
        record = options['metadata_id']

        if record == "all":
            for metadata_entry in MetadataEntry.objects.all.order_by('entry_id'):
                export_metadata_file = MetadataRecordGenerator(metadata_entry)
                export_metadata_file.do()
        else:
            metadata_entry = MetadataEntry.objects.get(entry_id=record)
            export_metadata_file = MetadataRecordGenerator(metadata_entry)
            export_metadata_file.do()

class MetadataRecordGenerator:
    def __init__(self, metadata_entry):
        self.metadata_entry = metadata_entry
        self.xml_root = None

    @staticmethod
    def add_char_element(parent, tag, text):
        if text != "" and text is not None:
            element = etree.SubElement(parent, tag)
            element.text = text

    @staticmethod
    def add_date_element(parent, tag, date):
        if date is not None:
            element = etree.SubElement(parent, tag)
            element.text = date.strftime("%F")

    @staticmethod
    def add_personnel(parent, tag, personnel):
        for person in personnel.all():
            personnel_xml = etree.SubElement(parent, tag)

            for dataset_role in person.dataset_role.all():
                MetadataRecordGenerator.add_char_element(personnel_xml, "Role",
                                                         dataset_role.role)

            MetadataRecordGenerator.add_char_element(personnel_xml, "First_Name",
                                                     person.person.name_first)

            MetadataRecordGenerator.add_char_element(personnel_xml, "Middle_Name",
                                                     person.person.name_middle)

            MetadataRecordGenerator.add_char_element(personnel_xml, "Last_Name",
                                                     person.person.name_last)

    @staticmethod
    def add_parameters(parent, tag, parameters):
        for parameter in parameters.all():
            parameter_xml = etree.SubElement(parent, tag, attrib={'uuid': parameter.uuid})
            MetadataRecordGenerator.add_char_element(parameter_xml, 'Category', parameter.category)
            MetadataRecordGenerator.add_char_element(parameter_xml, 'Topic', parameter.topic)
            MetadataRecordGenerator.add_char_element(parameter_xml, 'Term', parameter.term)
            MetadataRecordGenerator.add_char_element(parameter_xml, 'Variable_Level_1', parameter.variable_level_1)
            MetadataRecordGenerator.add_char_element(parameter_xml, 'Variable_Level_2', parameter.variable_level_2)
            MetadataRecordGenerator.add_char_element(parameter_xml, 'Variable_Level_3', parameter.variable_level_3)

    @staticmethod
    def add_sensor_names(parent, tag, sensor_names):
        for sensor_name in sensor_names:
            sensor_name_xml = etree.SubElement(parent, tag) # , attrib={'uuid': sensor_name.uuid})
            MetadataRecordGenerator.add_char_element(sensor_name_xml, 'Short_Name', sensor_name.short_name)
            MetadataRecordGenerator.add_char_element(sensor_name_xml, 'Long_Name', sensor_name.long_name)


    @staticmethod
    def add_data_set_citation(parent, tag, data_set_citation):
        data_set_citation_xml = etree.SubElement(parent, tag)

        for creator in data_set_citation.dataset_creator.all():
            MetadataRecordGenerator.add_char_element(data_set_citation_xml, "Dataset_Creator",
                                                     "{} {}".format(creator.name_first, creator.name_last))


#        MetadataRecordGenerator.add_char_element(data_set_citation_xml, "Dataset_Creator",
#                              "{} {}".format(data_set_citation.dataset_creator.name_first, data_set_citation.dataset_creator.name_last))
        MetadataRecordGenerator.add_char_element(data_set_citation_xml, "Dataset_Title", data_set_citation.dataset_title)
        MetadataRecordGenerator.add_date_element(data_set_citation_xml, "Dataset_Release_Date", data_set_citation.dataset_release_date)

        if data_set_citation.dataset_publisher is not None:
            MetadataRecordGenerator.add_char_element(data_set_citation_xml, "Dataset_Publisher", data_set_citation.dataset_publisher.long_name)

        MetadataRecordGenerator.add_char_element(data_set_citation_xml, "Version", data_set_citation.version)
        MetadataRecordGenerator.add_char_element(data_set_citation_xml, "Other_Citation_Details", data_set_citation.other_citation_details)

    @staticmethod
    def add_sensor_names(parent, tag, sensor_names):
        for sensor_name in sensor_names:
            print(sensor_name.uuid)
            sensor_name_xml = etree.SubElement(parent, tag, {'uuid': sensor_name.uuid})
            MetadataRecordGenerator.add_char_element(sensor_name_xml, 'Short_Name', sensor_name.short_name)
            MetadataRecordGenerator.add_char_element(sensor_name_xml, 'Long_Name', sensor_name.long_name)

    @staticmethod
    def add_temporal_coverage(parent, tag, temporal_coverages):
        for temporal_coverage in temporal_coverages.all():
            temporal_coverage_xml = etree.SubElement(parent, tag)
            MetadataRecordGenerator.add_date_element(temporal_coverage_xml, 'Start_Date', temporal_coverage.start_date)
            MetadataRecordGenerator.add_date_element(temporal_coverage_xml, 'Stop_Date', temporal_coverage.stop_date)

    @staticmethod
    def add_location(parent, tag, locations):
        for location in locations.all():
            location_xml = etree.SubElement(parent, tag, {'uuid': location.uuid})
            MetadataRecordGenerator.add_char_element(location_xml, 'Location_Category', location.location_category)
            MetadataRecordGenerator.add_char_element(location_xml, 'Location_Type', location.location_type)
            MetadataRecordGenerator.add_char_element(location_xml, 'Location_Subregion1', location.location_subregion1)
            MetadataRecordGenerator.add_char_element(location_xml, 'Location_Subregion2', location.location_subregion2)
            MetadataRecordGenerator.add_char_element(location_xml, 'Location_Subregion3', location.location_subregion3)
            MetadataRecordGenerator.add_char_element(location_xml, 'detailed_location', location.detailed_location)


    @staticmethod
    def add_data_resolution(parent, tag, data_resolutions):
        for data_resolution in data_resolutions.all():
            data_resolution_xml = etree.SubElement(parent, tag)
            MetadataRecordGenerator.add_char_element(data_resolution_xml, 'Latitude_Resolution',
                                                     data_resolution.latitude_resolution)

            MetadataRecordGenerator.add_char_element(data_resolution_xml, 'Longitude_Resolution',
                                                     data_resolution.longitude_resolution)

            if data_resolution.horizontal_resolution_range is not None:
                MetadataRecordGenerator.add_char_element(data_resolution_xml, 'Horizontal_Resolution_Range',
                                                         data_resolution.horizontal_resolution_range.horizontal_resolution_range)

            if data_resolution.vertical_resolution_range is not None:
                MetadataRecordGenerator.add_char_element(data_resolution_xml, 'Vertical_Resolution_Range',
                                                         data_resolution.vertical_resolution_range.vertical_resolution_range)

            if data_resolution.temporal_resolution_range is not None:
                MetadataRecordGenerator.add_char_element(data_resolution_xml, 'Temporal_Resolution_Range',
                                                         data_resolution.temporal_resolution_range.temporal_resolution_range)

    @staticmethod
    def add_project(parent, tag, projects):
        for project in projects.all():
            project_xml = etree.SubElement(parent, tag, {'uuid': project.uuid})
            MetadataRecordGenerator.add_char_element(project_xml, 'Short_Name',
                                                     project.short_name)
            MetadataRecordGenerator.add_char_element(project_xml, 'Long_Name',
                                                     project.long_name)

    @staticmethod
    def add_spatial_coverage(parent, tag, spatial_coverages):
        for spatial_coverage in spatial_coverages.all():
            spatial_coverage_xml = etree.SubElement(parent, tag)
            MetadataRecordGenerator.add_char_element(spatial_coverage_xml,
                                                     'Southernmost_Latitude',
                                                     str(spatial_coverage.southernmost_latitude))
            MetadataRecordGenerator.add_char_element(spatial_coverage_xml,
                                                     'Northernmost_Latitude',
                                                     str(spatial_coverage.northernmost_latitude))
            MetadataRecordGenerator.add_char_element(spatial_coverage_xml,
                                                     'Westernmost_Longiutde',
                                                     str(spatial_coverage.westernmost_longitude))
            MetadataRecordGenerator.add_char_element(spatial_coverage_xml,
                                                     'Easternmost_Longitude',
                                                     str(spatial_coverage.easternmost_longitude))

            MetadataRecordGenerator.add_char_element(spatial_coverage_xml,
                                                     'Minimum_Altitude',
                                                     "{} meters".format(spatial_coverage.minimum_altitude))
            MetadataRecordGenerator.add_char_element(spatial_coverage_xml,
                                                     'Maximum_Altitude',
                                                     "{} meters".format(spatial_coverage.maximum_altitude))
            MetadataRecordGenerator.add_char_element(spatial_coverage_xml,
                                                     'Minimum_Depth',
                                                     "{} meters".format(spatial_coverage.minimum_depth))
            MetadataRecordGenerator.add_char_element(spatial_coverage_xml,
                                                     'Maximum_Depth',
                                                     "{} meters".format(spatial_coverage.maximum_depth))

    @staticmethod
    def add_data_center(parent, tag, data_centers):
        for data_center in data_centers.all():
            data_center_xml = etree.SubElement(parent, tag)

            data_center_name_xml = etree.SubElement(data_center_xml, 'Data_Center_Name')
            MetadataRecordGenerator.add_char_element(data_center_name_xml, 'Short_Name', data_center.data_center_name.short_name)
            MetadataRecordGenerator.add_char_element(data_center_name_xml, 'Long_Name', data_center.data_center_name.long_name)
            MetadataRecordGenerator.add_char_element(data_center_xml, 'Data_Set_Id', data_center.data_set_id)

            MetadataRecordGenerator.add_personnel(data_center_xml, 'Personnel', data_center.personnel)

    @staticmethod
    def add_summary(parent, tag, summary):
        summary_xml = etree.SubElement(parent, tag)
        MetadataRecordGenerator.add_char_element(summary_xml, 'Abstract', summary.abstract)
        MetadataRecordGenerator.add_char_element(summary_xml, 'Purpose', summary.purpose)

    @staticmethod
    def add_distribution(parent, tag, distributions):
        for distribution in distributions.all():
            distribution_xml = etree.SubElement(parent, tag)

            MetadataRecordGenerator.add_char_element(distribution_xml, 'Distribution_Media', distribution.distribution_media.distribution_media)
            MetadataRecordGenerator.add_char_element(distribution_xml, 'Distribution_Size', distribution.distribution_size)

            for distribution_format in distribution.distribution_format.all():
                MetadataRecordGenerator.add_char_element(distribution_xml, 'Distribution_Format', distribution_format.distribution_format)

            MetadataRecordGenerator.add_char_element(distribution_xml, 'Fees', distribution.fees)

    @staticmethod
    def add_parent_difs(parent, tag, parent_difs):
        for parent_dif in parent_difs.all():
            MetadataRecordGenerator.add_char_element(parent, tag, parent_dif.entry_id)

    @staticmethod
    def add_idn_nodes(parent, tag, idn_nodes):
        for idn_node in idn_nodes.all():
            idn_node_xml = etree.SubElement(parent, tag)
            MetadataRecordGenerator.add_char_element(idn_node_xml, 'Short_Name', idn_node.idn_node_short_name)
            MetadataRecordGenerator.add_char_element(idn_node_xml, 'Long_Name', idn_node.idn_node_long_name)

    def do(self):
        fp = open("/tmp/test_dif.xml", "wb")

        nsmap = {None: "http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/",
                 "xsi": "http://www.w3.org/2001/XMLSchema-instance",
                 "schemaLocation": "http://gcmd.nasa.gov/Aboutus/xml/dif/dif_v9.7.1.xsd"
                 }
        xml_root = etree.Element("DIF", nsmap=nsmap)

        MetadataRecordGenerator.add_char_element(xml_root, 'Entry_ID', self.metadata_entry.entry_id)
        MetadataRecordGenerator.add_char_element(xml_root, 'Entry_Title', self.metadata_entry.entry_title)
        MetadataRecordGenerator.add_data_set_citation(xml_root, 'Data_Set_Citation', self.metadata_entry.data_set_citation)
        MetadataRecordGenerator.add_personnel(xml_root, 'Personnel', self.metadata_entry.personnel)
        MetadataRecordGenerator.add_parameters(xml_root, 'Parameters', self.metadata_entry.parameters)
        MetadataRecordGenerator.add_sensor_names(xml_root, 'Sensor_Name', self.metadata_entry.sensor_names())
        # TODO: Source Name
        MetadataRecordGenerator.add_temporal_coverage(xml_root, 'Temporal_Coverage', self.metadata_entry.temporal_coverage)
        MetadataRecordGenerator.add_char_element(xml_root, 'Data_Set_Progress', self.metadata_entry.data_set_progress.type)
        MetadataRecordGenerator.add_spatial_coverage(xml_root, 'Spatial_Coverage', self.metadata_entry.spatial_coverage)
        MetadataRecordGenerator.add_location(xml_root, 'Location', self.metadata_entry.location)
        MetadataRecordGenerator.add_data_resolution(xml_root, 'Data_Resolution', self.metadata_entry.data_resolution)
        MetadataRecordGenerator.add_project(xml_root, 'Project', self.metadata_entry.project)
        MetadataRecordGenerator.add_data_center(xml_root, 'Data_Center', self.metadata_entry.data_centers)
        MetadataRecordGenerator.add_distribution(xml_root, 'Distribution', self.metadata_entry.distribution_set)
        MetadataRecordGenerator.add_summary(xml_root, 'Summary', self.metadata_entry.summary)

        MetadataRecordGenerator.add_char_element(xml_root, 'Quality', self.metadata_entry.quality)
        MetadataRecordGenerator.add_char_element(xml_root, 'Access_Constraints', self.metadata_entry.access_constraints)
        MetadataRecordGenerator.add_char_element(xml_root, 'Use_Constraints', self.metadata_entry.use_constraints)
        MetadataRecordGenerator.add_char_element(xml_root, 'Data_Set_Language', self.metadata_entry.data_set_language)
#        MetadataRecordGenerator.add_char_element(xml_root, 'Originating_Center', self.metadata_entry.originating_center)
        MetadataRecordGenerator.add_parent_difs(xml_root, 'Parent_DIF', self.metadata_entry.parent_difs)
        MetadataRecordGenerator.add_idn_nodes(xml_root, 'IDN_Node', self.metadata_entry.idn_node)
        MetadataRecordGenerator.add_char_element(xml_root, 'Metadata_Name', self.metadata_entry.metadata_name)
        MetadataRecordGenerator.add_char_element(xml_root, 'Metadata_Version', self.metadata_entry.metadata_version)
        MetadataRecordGenerator.add_date_element(xml_root, 'DIF_Creation_Date', self.metadata_entry.dif_creation_date)
        MetadataRecordGenerator.add_date_element(xml_root, 'Last_DIF_Revision_Date', self.metadata_entry.last_dif_revision_date)
        MetadataRecordGenerator.add_char_element(xml_root, 'Dif_Revision_History', self.metadata_entry.dif_revision_history)
        MetadataRecordGenerator.add_date_element(xml_root, 'Future_DIF_Review_Date', self.metadata_entry.future_dif_review_date)
#        MetadataRecordGenerator.add_data_set_citation(xml_root, 'Data_Set_Citation', self.metadata_entry.data_set_citation)
#        MetadataRecordGenerator.add_sensor_names(xml_root, 'Sensor_Name', self.metadata_entry.sensor_name)



        b = etree.tostring(xml_root, pretty_print=True)
        print(b.decode('utf-8'))
        fp.write(b)
        fp.close()