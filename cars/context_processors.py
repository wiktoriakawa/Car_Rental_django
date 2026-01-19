from .models import Car

def get_all_brands(request): 
# funkcja ktora pobiera wszystkie unikalne marki samochodow z bazy danych
    
    brands = Car.objects.values_list('brand', flat=True).distinct().order_by('brand')
    return {'all_brands': brands}