from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("bookings/<int:booking_id>/finish/", views.finish_rental_summary, name="finish_rental_summary"),
    path("bookings/<int:booking_id>/finish/confirm/", views.finish_rental_confirm, name="finish_rental_confirm"),


]
