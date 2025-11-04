from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from weather_app.views import CityViewSet, WeatherRecordViewSet


router = DefaultRouter()
router.register(r'cities', CityViewSet, basename='city')
router.register(r'weather-records', WeatherRecordViewSet, basename='weather-record')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]