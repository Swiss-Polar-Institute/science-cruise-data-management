from django.test import TestCase
from django.test import Client

class SunsetSunriseTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get(self):
        response = self.client.get("/sunset_sunrise/")
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post("/sunset_sunrise/", {"latitude": 53, "longitude": -3, "date": "2019-05-03"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2019-05-03")
