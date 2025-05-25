from rest_framework import serializers
from .models import Settings, OpeningHour

class OpeningHourSerializer(serializers.ModelSerializer):
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    class Meta:
        model = OpeningHour
        fields = ['id', 'day_of_week', 'day_of_week_display', 'opening_time', 'closing_time', 'is_open', 'is_holiday']

class SettingsSerializer(serializers.ModelSerializer):
    """
    Serializer para o model Settings.
    """
    opening_hours = OpeningHourSerializer(many=True, read_only=True)
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