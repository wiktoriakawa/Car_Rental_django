from django import views
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from pages import views as pages_views
from cars import views as cars_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('pages.urls')),
    path('cars/', include('cars.urls')), 
    path('api/v1/cars/', cars_views.CarListAPIView.as_view(), name='api_car_list'),
    path('api/v1/teams/', pages_views.TeamListAPIView.as_view(), name='api_team_list'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)