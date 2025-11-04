from rest_framework import serializers
from .models import City, WeatherRecord


class CitySerializer(serializers.ModelSerializer):
    weather_records_count = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = ['id', 'name', 'country', 'latitude', 'longitude', 
                  'created_at', 'updated_at', 'weather_records_count']
        read_only_fields = ['created_at', 'updated_at']

    def get_weather_records_count(self, obj):
        return obj.weather_records.count()


class WeatherRecordSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)

    class Meta:
        model = WeatherRecord
        fields = ['id', 'city', 'city_name', 'temperature', 'feels_like', 
                  'humidity', 'pressure', 'wind_speed', 'description', 
                  'recorded_at', 'created_at']
        read_only_fields = ['created_at']


class WeatherRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherRecord
        fields = ['city', 'temperature', 'feels_like', 'humidity', 
                  'pressure', 'wind_speed', 'description', 'recorded_at']


class CityDetailSerializer(serializers.ModelSerializer):
    recent_weather = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = ['id', 'name', 'country', 'latitude', 'longitude', 
                  'created_at', 'updated_at', 'recent_weather']

    def get_recent_weather(self, obj):
        recent_records = obj.weather_records.all()[:5]
        return WeatherRecordSerializer(recent_records, many=True).data