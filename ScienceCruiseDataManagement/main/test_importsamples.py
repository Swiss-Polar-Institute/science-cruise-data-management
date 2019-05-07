from django.test import TransactionTestCase

from main.models import Ship, Mission, Leg, Project, Person, Event, ImportedFile, Organisation, Country, Leg, Port,\
    SamplingMethod, Platform, PlatformType

from django.core.exceptions import ObjectDoesNotExist

import datetime


class ImportSamplesTest(TransactionTestCase):
    def setUp(self):
        try:
            country = Country.objects.get(name="Switzerland")
        except ObjectDoesNotExist:
            country = Country()
            country.name = "Switzerland"
            country.save()

        try:
            organisation = Organisation.objects.get(name="SPI")
        except ObjectDoesNotExist:
            organisation = Organisation()
            organisation.name = "SPI"
            organisation.country = country
            organisation.save()

        try:
            mission = Mission.objects.get(name="GLACE")
        except ObjectDoesNotExist:
            mission = Mission()
            mission.name = "GLACE"
            mission.institution = organisation
            mission.save()

        # sample.mission = mission

        try:
            start_port_country = Country.objects.get(name="Germany")
        except ObjectDoesNotExist:
            start_port_country = Country()
            start_port_country.name = "Germany"
            start_port_country.save()

        try:
            start_port = Port.objects.get(name="Kiel")
        except ObjectDoesNotExist:
            start_port = Port()
            start_port.name = "Kiel"
            start_port.country = start_port_country
            start_port.latitude = 53
            start_port.longitude = 10
            start_port.save()

        try:
            end_port = Port.objects.get(name="Kiel")
        except ObjectDoesNotExist:
            end_port = Port()
            end_port.name = "Reijkavik"
            end_port.country = start_port_country
            end_port.save()

        try:
            leg = Leg.objects.get(number=1)
        except ObjectDoesNotExist:
            leg = Leg()
            leg.number = 1
            leg.start_date_time = datetime.datetime(2019, 7, 25)
            leg.start_port = start_port
            leg.end_port = end_port
            leg.save()

        # sample.leg = leg

        try:
            project = Project.objects.get(number=1)
        except ObjectDoesNotExist:
            project = Project()
            project.number = 1
            project.mission = mission
            project.save()

        # sample.project = project

        # sample.julian_day = 180

        try:
            sampling_method = SamplingMethod.objects.get(name="Getting soil")
        except ObjectDoesNotExist:
            sampling_method = SamplingMethod()
            sampling_method.name = "Getting soil"
            sampling_method.save()

        event = Event()
        event.sampling_method = sampling_method
        event.data = False
        event.samples = True
        event.save()

        try:
            pi = Person.objects.get(name_first="Jen", name_last="Thomas")
        except ObjectDoesNotExist:
            pi = Person()
            pi.name_first = "Jen"
            pi.name_last = "Thomas"
            pi.save()

        # sample.pi = pi
        # sample.event = event

        try:
            platform_type = PlatformType.objects.get(name="Ship")
        except ObjectDoesNotExist:
            platform_type = PlatformType()
            platform_type.name = "Ship"
            platform_type.save()

        try:
            platform = Platform.objects.get(name="AT")
        except ObjectDoesNotExist:
            platform = Platform()
            platform.name = "AT"
            platform.uuid = "askdkasdkf"
            platform.platform_type = platform_type
            platform.save()

        try:
            ship = Ship.objects.get(shortened_name="AT")
        except ObjectDoesNotExist:
            ship = Ship()
            ship.shortened_name = "AT"
            ship.name = platform
            ship.save()

        # sample.ship = ship
        # sample.contents = "This is the first test"

        # d = {"color": "red", "temperature_collection": 55}
        # sample.other_data = d

    def test_utils_coordinates_process_invalid_coordinates(self):
        template_information = {}
