from django.http import HttpResponse  # ADD THIS IMPORT
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

# Homepage function
def home(request):
    # Get counts from database
    city_count = City.objects.count()
    weather_count = WeatherRecord.objects.count()
    
    # Get recent cities
    recent_cities = City.objects.all()[:5]
    cities_html = ""
    for city in recent_cities:
        cities_html += f'<div class="card-item">📍 {city.name}, {city.country}</div>'
    
    if not cities_html:
        cities_html = '<div class="card-item">No cities yet. Use the API to add some!</div>'
    
    # Get recent weather records
    recent_weather = WeatherRecord.objects.select_related('city').order_by('-recorded_at')[:5]
    weather_html = ""
    for record in recent_weather:
        weather_html += f'<div class="card-item">🌡️ {record.city.name}: {record.temperature}°C - {record.description}</div>'
    
    if not weather_html:
        weather_html = '<div class="card-item">No weather data yet. Fetch some using the API!</div>'
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Weather Analytics Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{
                text-align: center;
                padding: 40px 20px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                backdrop-filter: blur(10px);
                margin-bottom: 30px;
            }}
            h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
            .stats {{
                display: flex;
                gap: 20px;
                justify-content: center;
                flex-wrap: wrap;
                margin: 30px 0;
            }}
            .stat-card {{
                background: rgba(255, 255, 255, 0.2);
                padding: 20px 40px;
                border-radius: 10px;
                text-align: center;
            }}
            .stat-number {{
                font-size: 2.5em;
                font-weight: bold;
                color: #ffd700;
            }}
            .stat-label {{ font-size: 0.9em; opacity: 0.9; }}
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .card {{
                background: rgba(255, 255, 255, 0.1);
                padding: 25px;
                border-radius: 10px;
                backdrop-filter: blur(10px);
            }}
            .card h2 {{ margin-bottom: 15px; font-size: 1.3em; }}
            .card-item {{
                background: rgba(0, 0, 0, 0.2);
                padding: 12px;
                margin: 8px 0;
                border-radius: 5px;
                font-size: 0.95em;
            }}
            .endpoint-link {{
                display: block;
                background: rgba(255, 255, 255, 0.2);
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                color: white;
                text-decoration: none;
                transition: all 0.3s;
            }}
            .endpoint-link:hover {{
                background: rgba(255, 255, 255, 0.3);
                transform: translateX(5px);
            }}
            .badge {{
                background: #28a745;
                padding: 4px 10px;
                border-radius: 4px;
                font-size: 0.75em;
                margin-left: 10px;
                font-weight: bold;
            }}
            .btn {{
                display: inline-block;
                background: #ffd700;
                color: #764ba2;
                padding: 12px 30px;
                border-radius: 25px;
                text-decoration: none;
                font-weight: bold;
                margin: 10px;
                transition: all 0.3s;
            }}
            .btn:hover {{
                background: #ffed4e;
                transform: scale(1.05);
            }}
            .code-block {{
                background: rgba(0, 0, 0, 0.4);
                padding: 15px;
                border-radius: 8px;
                overflow-x: auto;
                margin: 15px 0;
                font-family: monospace;
                font-size: 0.9em;
            }}
            .footer {{
                text-align: center;
                padding: 30px;
                opacity: 0.9;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌤️ Weather Analytics Dashboard</h1>
                <p style="font-size: 1.1em; margin-top: 10px;">Real-time weather data tracking and analytics API</p>
                
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">{city_count}</div>
                        <div class="stat-label">Cities Tracked</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{weather_count}</div>
                        <div class="stat-label">Weather Records</div>
                    </div>
                </div>
                
                <div style="margin-top: 20px;">
                    <a href="/api/" class="btn">🔌 Explore API</a>
                    <a href="/admin/" class="btn">⚙️ Admin Panel</a>
                </div>
            </div>

            <div class="grid">
                <div class="card">
                    <h2>🌆 Recent Cities</h2>
                    {cities_html}
                </div>
                
                <div class="card">
                    <h2>🌡️ Latest Weather Data</h2>
                    {weather_html}
                </div>
            </div>

            <div class="card">
                <h2>📍 API Endpoints</h2>
                <a href="/api/" class="endpoint-link">
                    🏠 API Root<span class="badge">GET</span>
                    <br><small>/api/</small>
                </a>
                <a href="/api/cities/" class="endpoint-link">
                    🌆 Cities Management<span class="badge">GET/POST</span>
                    <br><small>/api/cities/</small>
                </a>
                <a href="/api/weather-records/" class="endpoint-link">
                    🌡️ Weather Records<span class="badge">GET/POST</span>
                    <br><small>/api/weather-records/</small>
                </a>
                <a href="/api/weather-records/analytics/" class="endpoint-link">
                    📊 Analytics & Reports<span class="badge">GET</span>
                    <br><small>/api/weather-records/analytics/</small>
                </a>
            </div>

            <div class="card">
                <h2>🚀 Quick Start</h2>
                <p style="margin-bottom: 15px;">Test the API with these commands:</p>
                
                <h3 style="margin-top: 20px; margin-bottom: 10px;">1. Create a City</h3>
                <div class="code-block">
curl -X POST {request.build_absolute_uri('/api/cities/')} \\<br>
&nbsp;&nbsp;-H "Content-Type: application/json" \\<br>
&nbsp;&nbsp;-d '{{"name": "Mumbai", "country": "India", "latitude": 19.0760, "longitude": 72.8777}}'
                </div>
                
                <h3 style="margin-top: 20px; margin-bottom: 10px;">2. Fetch Weather Data</h3>
                <div class="code-block">
curl -X POST {request.build_absolute_uri('/api/cities/1/fetch_weather/')}
                </div>
                
                <h3 style="margin-top: 20px; margin-bottom: 10px;">3. View Analytics</h3>
                <div class="code-block">
curl {request.build_absolute_uri('/api/weather-records/analytics/')}
                </div>
            </div>

            <div class="footer">
                <p>Built with Django • PostgreSQL • OpenWeatherMap API</p>
                <p style="margin-top: 10px;">
                    <a href="https://github.com/Vicky9022/weather-analytics-dashboard" style="color: #ffd700;">📦 View on GitHub</a>
                </p>
                <p style="margin-top: 15px; font-size: 0.85em;">
                    💡 Tip: Use the browsable API at <a href="/api/" style="color: #ffd700;">/api/</a> for interactive testing
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)


# City ViewSet - DEFINE ONLY ONCE
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
        
        url = "http://api.openweathermap.org/data/2.5/weather"
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


# Weather Record ViewSet
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

        stats = queryset.aggregate(
            avg_temperature=Avg('temperature'),
            max_temperature=Max('temperature'),
            min_temperature=Min('temperature'),
            avg_humidity=Avg('humidity'),
            avg_pressure=Avg('pressure'),
            avg_wind_speed=Avg('wind_speed'),
            total_records=Count('id')
        )

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