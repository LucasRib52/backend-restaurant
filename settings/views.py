from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Settings, OpeningHour
from .serializers import SettingsSerializer, OpeningHourSerializer
import json

# Create your views here.

class SettingsDetailView(generics.RetrieveUpdateAPIView):
    """
    API para recuperar e atualizar as configurações do usuário logado.
    Apenas o próprio usuário pode acessar/alterar suas configurações.
    """
    serializer_class = SettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Retorna as configurações do usuário logado, cria se não existir
        obj, created = Settings.objects.get_or_create(
            user=self.request.user,
            defaults={
                "business_name": "Meu Negócio",
                "business_phone": "",
                "business_address": "",
                "business_email": "",
                "opening_time": "08:00",
                "closing_time": "18:00",
                "is_open": True,
                "delivery_available": True,
                "delivery_fee": 0,
                "minimum_order_value": 0,
                "tax_rate": 0,
            }
        )
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Atualiza os horários de funcionamento se enviados
        opening_hours_data = request.data.get('opening_hours')
        if opening_hours_data:
            # Se vier como string (por multipart), faz o parse
            if isinstance(opening_hours_data, str):
                opening_hours_data = json.loads(opening_hours_data)
            instance.opening_hours.all().delete()
            for oh in opening_hours_data:
                OpeningHour.objects.create(settings=instance, **oh)

        return Response(serializer.data)
