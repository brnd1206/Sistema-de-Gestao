# sgea_app/serializers.py

from rest_framework import serializers
from .models import Evento, Inscricao

class EventoSerializer(serializers.ModelSerializer):
    # Exibe o nome do organizador em vez do ID
    organizador = serializers.StringRelatedField()

    class Meta:
        model = Evento
        fields = ['id', 'nome', 'data_inicio', 'local', 'organizador']

class InscricaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inscricao
        fields = ['evento'] # O usuário envia apenas o ID do evento

    def create(self, validated_data):
        # A lógica de pegar o usuário logado será feita na View
        return Inscricao.objects.create(**validated_data)