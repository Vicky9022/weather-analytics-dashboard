from django.db import models

from django.db import models
from django.utils import timezone

class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cities'
        verbose_name_plural = 'Cities'
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.country}"


class WeatherRecord(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='weather_records')
    temperature = models.FloatField(help_text="Temperature in Celsius")
    feels_like = models.FloatField(help_text="Feels like temperature in Celsius")
    humidity = models.IntegerField(help_text="Humidity percentage")
    pressure = models.IntegerField(help_text="Atmospheric pressure in hPa")
    wind_speed = models.FloatField(help_text="Wind speed in m/s")
    description = models.CharField(max_length=200)
    recorded_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'weather_records'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['-recorded_at']),
            models.Index(fields=['city', '-recorded_at']),
        ]

    def __str__(self):
        return f"{self.city.name} - {self.temperature}°C at {self.recorded_at}"
