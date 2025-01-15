from django.test import TestCase
from django.urls import reverse

from xabber_plugins.models import Plugin, Track, Release
from xabber_plugins.custom_auth.models import Developer

from datetime import datetime


class PluginListViewTests(TestCase):

    def setUp(self):
        # Create some items in the database to test the API
        self.developer = Developer.objects.create_user(
            username='testdeveloper',
            password='test1234',
            email='developer@test.com'
        )
        self.free_track = Track.objects.create(name='free')
        self.paid_track = Track.objects.create(name='paid')
        self.first_plugin = Plugin.objects.create(
            name='xabber_test',
            display_name='Xabber Test',
            description='Description',
            developer=self.developer
        )

        today = datetime.today()
        year = today.year % 100  # last two digits of the year
        month = today.month
        self.first_release_first_plugin = Release.objects.create(
            version=f'{year:02}.{month:02}',
            plugin=self.first_plugin,
            track=self.free_track,
            xabber_server_versions=[1]
        )
        self.second_release_first_plugin = Release.objects.create(
            version=f'{year:02}.{month:02}.1',
            plugin=self.first_plugin,
            track=self.free_track,
            xabber_server_versions=[2]
        )

        self.second_plugin = Plugin.objects.create(
            name='xabber_test2',
            display_name='Xabber Test 2',
            description='Description',
            developer=self.developer
        )
        self.first_release_second_plugin = Release.objects.create(
            version=f'{year:02}.{month:02}',
            plugin=self.second_plugin,
            track=self.free_track,
            xabber_server_versions=[1]
        )
        self.second_release_second_plugin = Release.objects.create(
            version=f'{year:02}.{month:02}.1',
            plugin=self.second_plugin,
            track=self.free_track,
            xabber_server_versions=[2]
        )

        self.url = reverse('api:plugins')

    def test_plugin_list_success(self):
        # Test that the list view returns a 200 status code

        response = self.client.get(self.url)
        response_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('count', response_data)
        self.assertEqual(2, response_data.get('count'))

        self.assertIn('result', response_data)
        self.assertEqual('xabber_test', response_data.get('result')[0].get('name'))
        self.assertEqual('xabber_test2', response_data.get('result')[1].get('name'))

    def test_plugin_list_with_arguments(self):
        data = {
            'name': self.first_plugin.name,
            'xabber_server_version': 1
        }

        response = self.client.get(self.url, data=data)
        response_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('count', response_data)
        self.assertEqual(1, response_data.get('count'))

        self.assertIn('result', response_data)
        self.assertEqual('xabber_test', response_data.get('result')[0].get('name'))

        today = datetime.today()
        year = today.year % 100  # last two digits of the year
        month = today.month
        self.assertEqual(f'{year:02}.{month:02}', response_data.get('result')[0].get('release'))

    def test_plugin_list_unexisting_plugin_name(self):
        data = {
            'name': 'unexisting_name',
            'xabber_server_version': 1
        }

        response = self.client.get(self.url, data=data)
        response_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('count', response_data)
        self.assertEqual(0, response_data.get('count'))

    def test_plugin_list_with_pagination(self):
        data = {
            'page_size': 1,
        }

        response = self.client.get(self.url, data=data)
        response_data = response.json()
        self.assertEqual(response.status_code, 200)

        self.assertIn('next', response_data)

        response = self.client.get(response_data.get('next'))
        response_data = response.json()
        self.assertEqual(response.status_code, 200)

        self.assertIn('previous', response_data)
