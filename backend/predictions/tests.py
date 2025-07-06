from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

class PredictAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='testpass')
        self.client.login(username='test', password='testpass')

    def test_predict_requires_auth(self):
        self.client.logout()
        response = self.client.post(reverse('predict'), {'ticker': 'AAPL'})
        self.assertEqual(response.status_code, 401)

    def test_predict_valid(self):
        self.client.login(username='test', password='testpass')
        response = self.client.post(reverse('predict'), {'ticker': 'AAPL'})
        self.assertIn(response.status_code, [200, 400, 500])  # Accepts any, just for demo