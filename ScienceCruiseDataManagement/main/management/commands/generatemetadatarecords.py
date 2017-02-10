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
        pass


    def create_all_records(self):
        print("create all records")
        root = etree.Element("DIF")
        root.append(etree.Element("child1"))
        child2 = etree.SubElement(root, "child2")
        child3 = etree.SubElement(root, "child3")

        b = etree.tostring(root, pretty_print=True)
        print(b.decode('utf-8'))
