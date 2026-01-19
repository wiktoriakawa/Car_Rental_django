from django.db import models
from ckeditor.fields import RichTextField
from multiselectfield import MultiSelectField
from django.utils.text import slugify
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.conf import settings


# Create your models here.

# Wszystkie _CHOICES zostały wygenerowane za pomocą AI
class Car(models.Model):

    # wygenerowane przez AI
    STATE_CHOICES = (
    ("wroclaw", "Wrocław"),
    ("lublin", "Lublin"),
    ("krakow", "Kraków"),
    ("warszawa", "Warszawa"),
    ("rzeszow", "Rzeszów"),
    ("bialystok", "Białystok"),
    ("gdansk", "Gdańsk"),
    ("kielce", "Kielce"),
    ("poznan", "Poznań"),
    ("szczecin", "Szczecin"),
    )

    YEAR_CHOICES = [(r, r) for r in range(2000, 2027)]

    FEATURES_CHOICES = (
    # wygenerowane przez AI 
    ("air_conditioning", "Klimatyzacja"),
    ("automatic_climate", "Klimatyzacja automatyczna"),
    ("heated_seats", "Podgrzewane siedzenia"),
    ("electric_seats", "Elektrycznie regulowane siedzenia"),
    ("leather_seats", "Skórzana tapicerka"),
    ("armrest", "Podłokietnik"),
    ("keyless", "Dostęp bezkluczykowy"),
    ("push_start", "Start/Stop Engine"),
    ("bluetooth", "Bluetooth"),
    ("usb", "USB"),
    ("aux", "AUX"),
    ("apple_carplay", "Apple CarPlay"),
    ("android_auto", "Android Auto"),
    ("navigation", "Nawigacja GPS"),
    ("touchscreen", "Ekran dotykowy"),
    ("premium_audio", "Nagłośnienie premium"),

    # Bezpieczeństwo
    ("abs", "ABS"),
    ("esp", "ESP"),
    ("traction_control", "Kontrola trakcji"),
    ("lane_assist", "Asystent pasa ruchu"),
    ("blind_spot", "Czujnik martwego pola"),
    ("adaptive_cruise", "Adaptacyjny tempomat"),
    ("emergency_brake", "Automatyczne hamowanie awaryjne"),
    ("airbags", "Poduszki powietrzne"),

    # Parkowanie
    ("parking_sensors_front", "Czujniki parkowania przód"),
    ("parking_sensors_rear", "Czujniki parkowania tył"),
    ("parking_camera", "Kamera cofania"),
    ("360_camera", "Kamera 360°"),
    ("auto_parking", "Asystent parkowania"),

    # Napęd / skrzynia
    ("automatic", "Automatyczna skrzynia biegów"),
    ("manual", "Manualna skrzynia biegów"),
    ("awd", "Napęd 4x4"),
    ("hybrid", "Napęd hybrydowy"),
    ("electric", "Samochód elektryczny"),

    # Dodatki
    ("cruise_control", "Tempomat"),
    ("panoramic_roof", "Panoramiczny dach"),
    ("sunroof", "Szyberdach"),
    ("roof_rack", "Bagażnik dachowy"),
    ("tow_hook", "Hak holowniczy"),
    ("winter_tires", "Opony zimowe"),
    ("child_seat", "Fotelik dziecięcy"),
    ("isofix", "ISOFIX"),
    )

    DOORS_CHOICES = (
    (2, "2 Dźwiowy"),
    (3, "3 Dźwiowy"),
    (4, "4 Dźwiowy"),
    (5, "5 Dźwiowy"),
    )

    car_title = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    year = models.IntegerField(choices=YEAR_CHOICES)
    image = models.ImageField(upload_to='cars/%Y/%m/%d/')
    created_at = models.DateTimeField(auto_now_add=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, choices=STATE_CHOICES)
    price = models.IntegerField()
    description = RichTextField()
    condition = models.CharField(max_length=50)
    features = MultiSelectField(choices=FEATURES_CHOICES)
    body_style = models.CharField(max_length=50)
    engine = models.CharField(max_length=100)
    transmission = models.CharField(max_length=50)
    interior = models.CharField(max_length=50)
    doors = models.IntegerField(choices=DOORS_CHOICES)
    passengers = models.IntegerField()
    milage = models.IntegerField()
    fuel_type = models.CharField(max_length=50)
    slug = models.SlugField(max_length=200, unique=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.brand}-{self.car_title}-{self.year}")
            slug = base
            i = 1
            while Car.objects.filter(slug=slug).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("car_detail", args=[self.id])

    def __str__(self):
        return self.car_title
    


class Booking(models.Model):
    STATUS_CHOICES = (
        ("pending", "Oczekująca"),
        ("confirmed", "Potwierdzona"),
        ("cancelled", "Anulowana"),
        ("finished", "Zakończona"),
    )

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="bookings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    start_date = models.DateField()
    end_date = models.DateField()

    total_price = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)

    actual_end_date = models.DateField(null=True, blank=True)
    final_price = models.IntegerField(null=True, blank=True)


    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError("Data zakończenia musi być po dacie rozpoczęcia.")

        overlapping = Booking.objects.filter(
            car=self.car,
            status__in=["pending", "confirmed"],
            start_date__lte=self.end_date,
            end_date__gte=self.start_date,
        )
        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError("Samochód jest już zarezerwowany w tym terminie.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.car} | {self.start_date} – {self.end_date}"
