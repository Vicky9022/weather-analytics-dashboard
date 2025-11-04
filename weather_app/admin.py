from django.contrib import admin
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from weather_app.models import City, WeatherRecord


class CityAPITestCase(APITestCase):
    def setUp(self):
        self.city_data = {
            'name': 'Mumbai',
            'country': 'India',
            'latitude': 19.0760,
            'longitude': 72.8777
        }
        self.city = City.objects.create(**self.city_data)

    def test_create_city(self):
        """Test creating a new city"""
        data = {
            'name': 'Delhi',
            'country': 'India',
            'latitude': 28.6139,
            'longitude': 77.2090
        }
        response = self.client.post('/api/cities/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(City.objects.count(), 2)
        self.assertEqual(response.data['name'], 'Delhi')

    def test_list_cities(self):
        """Test listing all cities"""
        response = self.client.get('/api/cities/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_city_detail(self):
        """Test retrieving a specific city"""
        response = self.client.get(f'/api/cities/{self.city.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Mumbai')

    def test_update_city(self):
        """Test updating a city"""
        data = {'name': 'Mumbai City', 'country': 'India', 
                'latitude': 19.0760, 'longitude': 72.8777}
        response = self.client.put(f'/api/cities/{self.city.id}/', 
                                   data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.city.refresh_from_db()
        self.assertEqual(self.city.name, 'Mumbai City')

    def test_delete_city(self):
        """Test deleting a city"""
        response = self.client.delete(f'/api/cities/{self.city.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(City.objects.count(), 0)


class WeatherRecordAPITestCase(APITestCase):
    def setUp(self):
        self.city = City.objects.create(
            name='London',
            country='UK',
            latitude=51.5074,
            longitude=-0.1278
        )
        self.weather_data = {
            'city': self.city.id,
            'temperature': 15.5,
            'feels_like': 14.2,
            'humidity': 70,
            'pressure': 1013,
            'wind_speed': 5.2,
            'description': 'Cloudy',
            'recorded_at': timezone.now()
        }

    def test_create_weather_record(self):
        """Test creating a weather record"""
        response = self.client.post('/api/weather-records/', 
                                   self.weather_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WeatherRecord.objects.count(), 1)
        self.assertEqual(float(response.data['temperature']), 15.5)

    def test_list_weather_records(self):
        """Test listing weather records"""
        WeatherRecord.objects.create(city=self.city, **{
            k: v for k, v in self.weather_data.items() if k != 'city'
        })
        response = self.client.get('/api/weather-records/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_by_city(self):
        """Test filtering weather records by city"""
        WeatherRecord.objects.create(city=self.city, **{
            k: v for k, v in self.weather_data.items() if k != 'city'
        })
        response = self.client.get(
            f'/api/weather-records/?city_id={self.city.id}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_analytics_endpoint(self):
        """Test weather analytics endpoint"""
        # Create multiple records
        for i in range(5):
            WeatherRecord.objects.create(city=self.city, **{
                k: v for k, v in self.weather_data.items() if k != 'city'
            })
        
        response = self.client.get('/api/weather-records/analytics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('statistics', response.data)
        self.assertIn('daily_trends', response.data)
        self.assertEqual(response.data['statistics']['total_records'], 5)


class IntegrationTestCase(APITestCase):
    def test_full_workflow(self):
        """Test complete workflow: create city, fetch weather, get analytics"""
        # 1. Create a city
        city_data = {
            'name': 'Paris',
            'country': 'France',
            'latitude': 48.8566,
            'longitude': 2.3522
        }
        response = self.client.post('/api/cities/', city_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        city_id = response.data['id']

        # 2. Manually add weather record (since API call requires real key)
        weather_data = {
            'city': city_id,
            'temperature': 18.5,
            'feels_like': 17.0,
            'humidity': 65,
            'pressure': 1015,
            'wind_speed': 3.5,
            'description': 'Partly cloudy',
            'recorded_at': timezone.now()
        }
        response = self.client.post('/api/weather-records/', 
                                   weather_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 3. Get analytics
        response = self.client.get(
            f'/api/weather-records/analytics/?city_id={city_id}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['statistics']['average_temperature'])

        # 4. Get city with weather
        response = self.client.get(f'/api/cities/{city_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['recent_weather']), 1)
