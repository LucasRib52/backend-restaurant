from rest_framework import serializers
from .models import Settings, OpeningHour

class OpeningHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpeningHour
        fields = ['id', 'day_of_week', 'opening_time', 'closing_time', 'is_open', 'is_holiday']

class SettingsSerializer(serializers.ModelSerializer):
    """
    Serializer para o model Settings.
    """
    opening_hours = OpeningHourSerializer(many=True, read_only=True)
    business_photo = serializers.ImageField(required=False, allow_null=True)
    business_slug = serializers.SlugField(required=False, allow_null=True)
    
    class Meta:
        model = Settings
        fields = [
            'id',
            'business_name',
            'business_phone',
            'business_address',
            'business_email',
            'business_photo',
            'business_slug',
            'opening_time',
            'closing_time',
            'is_open',
            'delivery_available',
            'delivery_fee',
            'minimum_order_value',
            'tax_rate',
            'opening_hours',
        ]
        extra_kwargs = {
            'business_name': {'required': False},
            'business_phone': {'required': False},
            'business_address': {'required': False},
            'business_email': {'required': False},
            'business_photo': {'required': False},
            'opening_time': {'required': False},
            'closing_time': {'required': False},
            'delivery_fee': {'required': False},
            'minimum_order_value': {'required': False},
            'tax_rate': {'required': False},
        } 