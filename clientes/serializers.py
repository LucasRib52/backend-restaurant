from rest_framework import serializers
from settings.models import Settings, OpeningHour
from products.models import Category, Product, ProductIngredient, Ingredient, IngredientCategory
from django.conf import settings as django_settings

class OpeningHourSerializer(serializers.ModelSerializer):
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    class Meta:
        model = OpeningHour
        fields = ['id', 'day_of_week', 'day_of_week_display', 'opening_time', 'closing_time', 'is_open', 'is_holiday']

class SettingsSerializer(serializers.ModelSerializer):
    business_photo = serializers.SerializerMethodField()
    business_slug = serializers.CharField(read_only=True)
    opening_hours = OpeningHourSerializer(many=True, read_only=True)

    class Meta:
        model = Settings
        fields = [
            'business_name',
            'business_phone',
            'business_address',
            'business_email',
            'business_photo',
            'business_slug',
            'opening_hours',
            'delivery_available',
            'delivery_fee',
            'minimum_order_value',
            'tax_rate'
        ]

    def get_business_photo(self, obj):
        if obj.business_photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.business_photo.url)
            return f"{django_settings.MEDIA_URL}{obj.business_photo}"
        return None

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class ProductIngredientSerializer(serializers.ModelSerializer):
    ingredient = serializers.SerializerMethodField()

    class Meta:
        model = ProductIngredient
        fields = ['ingredient', 'is_required', 'max_quantity']

    def get_ingredient(self, obj):
        return {
            'id': obj.ingredient.id,
            'name': obj.ingredient.name,
            'price': str(obj.ingredient.price),
            'category': {
                'id': obj.ingredient.category.id if obj.ingredient.category else None,
                'name': obj.ingredient.category.name if obj.ingredient.category else None
            }
        }

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    image = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image', 'category_name', 'is_active', 'ingredients']

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return f"{django_settings.MEDIA_URL}{obj.image}"
        return None

    def get_ingredients(self, obj):
        product_ingredients = ProductIngredient.objects.filter(product=obj).select_related('ingredient', 'ingredient__category')
        return ProductIngredientSerializer(product_ingredients, many=True).data 