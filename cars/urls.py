from django.urls import include, path
from . import views

urlpatterns = [
    path("", views.cars, name="cars"),
    path("<int:id>/", views.car_detail, name="car_detail"),
    path("search/", views.cars_search, name="cars_search"),
    path("cars/", views.cars, name="cars"),
    path("<int:id>/book/", views.book_car, name="book_car"),
]
