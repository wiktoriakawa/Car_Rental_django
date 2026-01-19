from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from cars.models import Car, Booking
from .models import Team
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.timezone import localdate
from django.contrib.messages import get_messages
from rest_framework import generics
from .serializers import TeamSerializer

# --- strona główna ---
def home(request):
    teams = Team.objects.all()
    cars_qs = Car.objects.all().order_by("-created_at")

    # --- pobieranie wartości z GET ---
    q = request.GET.get("q", "").strip()
    brand = request.GET.get("brand", "").strip()
    city = request.GET.get("city", "").strip()
    fuel_type = request.GET.get("fuel_type", "").strip()
    year = request.GET.get("year", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()

    # --- filtrowanie ---
    if q:
        cars_qs = cars_qs.filter(
            Q(car_title__icontains=q) |
            Q(brand__icontains=q) |
            Q(city__icontains=q) |
            Q(description__icontains=q)
        )
    if brand:
        cars_qs = cars_qs.filter(brand__icontains=brand)
    if city:
        cars_qs = cars_qs.filter(city__icontains=city)
    if fuel_type:
        cars_qs = cars_qs.filter(fuel_type__icontains=fuel_type)
    if year and year.isdigit():
        cars_qs = cars_qs.filter(year=int(year))
    if min_price and min_price.isdigit():
        cars_qs = cars_qs.filter(price__gte=int(min_price))
    if max_price and max_price.isdigit():
        cars_qs = cars_qs.filter(price__lte=int(max_price))

    cars = cars_qs[:12]

    return render(request, "pages/home.html", {
        "teams": teams,
        "cars": cars,
        "values": request.GET,  
    })

# --- rejestracja ---
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        if not username or not email or not password1 or not password2:
            messages.error(request, "Uzupełnij wszystkie pola.")
            return render(request, "accounts/signup.html")

        if password1 != password2:
            messages.error(request, "Hasła nie są takie same.")
            return render(request, "accounts/signup.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Taki login już istnieje.")
            return render(request, "accounts/signup.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Ten email jest już użyty.")
            return render(request, "accounts/signup.html")

        try:
            validate_password(password1)
        except ValidationError as e:
            for msg in e.messages:
                messages.error(request, msg)
            return render(request, "accounts/signup.html")

        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        messages.success(request, "Konto utworzone")
        return redirect("home")

    return render(request, "accounts/signup.html")

# --- logowanie ---
def login_view(request):
    if request.method == "GET":
        list(get_messages(request)) 
        if request.GET.get("next"):
            messages.info(request, "Zaloguj się, aby zarezerwować samochód.")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Nieprawidłowy login lub hasło.")
            return render(request, "accounts/login.html")

        login(request, user)

        next_url = request.POST.get("next") or request.GET.get("next")
        if next_url:
            return redirect(next_url)
        return redirect("home")
    
    return render(request, "accounts/login.html")

def logout_view(request):
    logout(request)
    return redirect("home")

# --- profil ---
@login_required
def profile(request):
    bookings = (
        Booking.objects
        .filter(user=request.user)
        .select_related("car")
        .order_by("-created_at")
    )
    return render(request, "accounts/profile.html", {
        "bookings": bookings
    })

@login_required
def edit_profile(request):
    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get("first_name", "")
        user.last_name = request.POST.get("last_name", "")
        user.email = request.POST.get("email", "")
        user.save()
        messages.success(request, "Profil zaktualizowany.")
        return redirect("profile")

    return render(request, "accounts/edit_profile.html")

# --- ppodsumowanie wynajmu ---
@login_required
def finish_rental_summary(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related("car"),
        id=booking_id,
        user=request.user
    )

    if booking.status in ["cancelled", "finished"]:
        messages.info(request, "Ta rezerwacja jest już zakończona lub anulowana.")
        return redirect("profile")

    today = localdate()
    start_date = booking.start_date

    if today < start_date:
        # jezeli zwrot przed rozpoczęciem -> 0 PLN
        days = 0
        total = 0
    else:
        # (today - start_date).days +1, aby wliczyć dzień dzisiejszy
        delta = today - start_date
        days = delta.days + 1
        

        total = days * booking.car.price

    return render(request, "accounts/finish_rental.html", {
        "booking": booking,
        "days": days,
        "total": total,
    })

# potwierdzenie zwrotu
@login_required
def finish_rental_confirm(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related("car"),
        id=booking_id,
        user=request.user
    )

    if request.method != "POST":
        return redirect("finish_rental_summary", booking_id=booking.id)

    if booking.status in ["cancelled", "finished"]:
        messages.info(request, "Ta rezerwacja jest już zakończona lub anulowana.")
        return redirect("profile")

    today = localdate()
    booking.actual_end_date = today

    start_date = booking.start_date
    
    if today < start_date:
        final_price = 0
    else:
        delta = today - start_date
        days_used = delta.days + 1
        final_price = days_used * booking.car.price

    # jako kwota finalna
    booking.final_price = final_price
    booking.status = "finished"
    booking.save()

    messages.success(
        request,
        f"Wynajem zakończony pomyślnie. Ostateczna kwota do zapłaty: {booking.final_price} PLN."
    )
    return redirect("profile")

class TeamListAPIView(generics.ListAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer