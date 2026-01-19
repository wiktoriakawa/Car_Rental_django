from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import Car
from django.template.loader import render_to_string
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import redirect
from datetime import datetime
from .models import Booking
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from rest_framework import generics
from .serializers import CarSerializer

def cars(request):
    cars = Car.objects.all().order_by("-created_at")  

    q = request.GET.get("q", "").strip()
    brand = request.GET.get("brand", "").strip()
    city = request.GET.get("city", "").strip()
    fuel_type = request.GET.get("fuel_type", "").strip()
    year = request.GET.get("year", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()

    # filtrowanie 
    if q:
        cars = cars.filter(
            Q(car_title__icontains=q) |
            Q(brand__icontains=q) |
            Q(city__icontains=q) |
            Q(description__icontains=q)
        )

    if brand:
        cars = cars.filter(brand__icontains=brand)

    if city:
        cars = cars.filter(city__icontains=city)

    if fuel_type:
        cars = cars.filter(fuel_type__icontains=fuel_type)

    if year:
        if year.isdigit():
            cars = cars.filter(year=int(year))

    if min_price:
        if min_price.isdigit():
            cars = cars.filter(price__gte=int(min_price))

    if max_price:
        if max_price.isdigit():
            cars = cars.filter(price__lte=int(max_price))


    return render(request, "cars/cars.html", {"cars": cars, "values": request.GET})

def car_detail(request, id):
    car = get_object_or_404(Car, id=id)

    context = {
        "car": car
    }

    return render(request, "cars/car_detail.html", context)

def cars_search(request):
    qs = Car.objects.all().order_by("-created_at")

    keyword = request.GET.get("keyword", "").strip()
    brand = request.GET.get("brand", "").strip()
    state = request.GET.get("state", "").strip()
    year = request.GET.get("year", "").strip()

    if keyword:
        qs = qs.filter(car_title__icontains=keyword)
    if brand:
        qs = qs.filter(brand__iexact=brand)
    if state:
        qs = qs.filter(state=state)
    if year:
        qs = qs.filter(year=year)

    html = render_to_string(
        "cars/partials/car_list.html",
        {"cars": qs},
        request=request
    )

    return JsonResponse({"html": html})


@login_required
def book_car(request, id):
    car = get_object_or_404(Car, id=id)

    if request.method == "POST":
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        if not start_date or not end_date:
            messages.error(request, "Wybierz daty wynajmu.")
            return redirect(car.get_absolute_url())

        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()

        days = (end - start).days
        if days <= 0:
            messages.error(request, " Zakres dat powinien mieć więcej niż 0 dni.")
            return redirect(car.get_absolute_url())

        total_price = days * car.price

        booking = Booking(
            car=car,
            user=request.user if request.user.is_authenticated else None,
            start_date=start,
            end_date=end,
            total_price=total_price
        )

        try:
            booking.save()
            messages.success(request, "Rezerwacja została utworzona.")
        except ValidationError as e:
            messages.error(request, e.message)

        return redirect(car.get_absolute_url())
    
    return redirect(car.get_absolute_url())
    
class CarListAPIView(generics.ListAPIView):
    queryset = Car.objects.all().order_by('-created_at')
    serializer_class = CarSerializer

