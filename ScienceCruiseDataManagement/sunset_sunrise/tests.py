from django.test import TestCase
from django.test import Client



class SunsetSunriseRequestsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get(self):
        response = self.client.get("/sunset_sunrise/")
        self.assertEqual(response.status_code, 200)

    def test_post_ok(self):
        response = self.client.post("/sunset_sunrise/", {"latitude": 53, "longitude": -3, "date": "2019-05-03"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2019-05-03")

    def test_post_invalid_latitude(self):
        response = self.client.post("/sunset_sunrise/", {"latitude": "XX", "longitude": -4.2, "date": "2019-05-03"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Latitude and longitude need to be in decimal degrees.")


    def test_post_invalid_date(self):
        response = self.client.post("/sunset_sunrise/", {"latitude": 53.58, "longitude": -4.2, "date": "asdf03.05.19"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid date time. It needs to be YYYY-MM-DD")
