from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Max, Min, Count
from django.utils import timezone
from datetime import timedelta
import requests
import os

from .models import City, WeatherRecord
from .serializers import (
    CitySerializer, CityDetailSerializer,
    WeatherRecordSerializer, WeatherRecordCreateSerializer
)


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CityDetailSerializer
        return CitySerializer

    @action(detail=True, methods=['post'])
    def fetch_weather(self, request, pk=None):
        """
        Fetch current weather from OpenWeatherMap API and save to database
        """
        city = self.get_object()
        api_key = os.getenv('OPENWEATHER_API_KEY', 'your_api_key_here')
        
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': city.latitude,
            'lon': city.longitude,
            'appid': api_key,
            'units': 'metric'
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Create weather record from API data
            weather_record = WeatherRecord.objects.create(
                city=city,
                temperature=data['main']['temp'],
                feels_like=data['main']['feels_like'],
                humidity=data['main']['humidity'],
                pressure=data['main']['pressure'],
                wind_speed=data['wind']['speed'],
                description=data['weather'][0]['description'],
                recorded_at=timezone.now()
            )

            serializer = WeatherRecordSerializer(weather_record)
            return Response({
                'success': True,
                'message': 'Weather data fetched and saved successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        except requests.RequestException as e:
            return Response({
                'success': False,
                'error': f'Failed to fetch weather data: {str(e)}'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class WeatherRecordViewSet(viewsets.ModelViewSet):
    queryset = WeatherRecord.objects.select_related('city').all()
    serializer_class = WeatherRecordSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return WeatherRecordCreateSerializer
        return WeatherRecordSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        city_id = self.request.query_params.get('city_id')
        days = self.request.query_params.get('days')

        if city_id:
            queryset = queryset.filter(city_id=city_id)
        
        if days:
            try:
                days_int = int(days)
                start_date = timezone.now() - timedelta(days=days_int)
                queryset = queryset.filter(recorded_at__gte=start_date)
            except ValueError:
                pass

        return queryset

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """
        Get weather analytics and statistics
        """
        city_id = request.query_params.get('city_id')
        days = int(request.query_params.get('days', 7))
        
        start_date = timezone.now() - timedelta(days=days)
        queryset = WeatherRecord.objects.filter(recorded_at__gte=start_date)
        
        if city_id:
            queryset = queryset.filter(city_id=city_id)

        # Calculate statistics
        stats = queryset.aggregate(
            avg_temperature=Avg('temperature'),
            max_temperature=Max('temperature'),
            min_temperature=Min('temperature'),
            avg_humidity=Avg('humidity'),
            avg_pressure=Avg('pressure'),
            avg_wind_speed=Avg('wind_speed'),
            total_records=Count('id')
        )

        # Get daily averages for visualization
        daily_data = []
        for i in range(days):
            day_start = start_date + timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            day_records = queryset.filter(
                recorded_at__gte=day_start,
                recorded_at__lt=day_end
            )
            day_avg = day_records.aggregate(
                avg_temp=Avg('temperature'),
                avg_humidity=Avg('humidity')
            )
            daily_data.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'avg_temperature': round(day_avg['avg_temp'], 2) if day_avg['avg_temp'] else None,
                'avg_humidity': round(day_avg['avg_humidity'], 2) if day_avg['avg_humidity'] else None
            })

        # Get city-wise summary
        city_summary = []
        if not city_id:
            cities = City.objects.all()
            for city in cities:
                city_records = queryset.filter(city=city)
                if city_records.exists():
                    city_stats = city_records.aggregate(
                        avg_temp=Avg('temperature'),
                        count=Count('id')
                    )
                    city_summary.append({
                        'city_name': city.name,
                        'country': city.country,
                        'avg_temperature': round(city_stats['avg_temp'], 2),
                        'record_count': city_stats['count']
                    })

        return Response({
            'period': f'Last {days} days',
            'statistics': {
                'average_temperature': round(stats['avg_temperature'], 2) if stats['avg_temperature'] else None,
                'max_temperature': round(stats['max_temperature'], 2) if stats['max_temperature'] else None,
                'min_temperature': round(stats['min_temperature'], 2) if stats['min_temperature'] else None,
                'average_humidity': round(stats['avg_humidity'], 2) if stats['avg_humidity'] else None,
                'average_pressure': round(stats['avg_pressure'], 2) if stats['avg_pressure'] else None,
                'average_wind_speed': round(stats['avg_wind_speed'], 2) if stats['avg_wind_speed'] else None,
                'total_records': stats['total_records']
            },
            'daily_trends': daily_data,
            'city_summary': city_summary
        })
