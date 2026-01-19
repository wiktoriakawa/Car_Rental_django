from rest_framework import serializers
from .models import Team

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        # Pobieramy wszystkie pola modelu Team
        fields = '__all__'