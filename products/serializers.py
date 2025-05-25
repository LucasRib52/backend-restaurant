from rest_framework import serializers
from .models import Category, Product, Ingredient, ProductIngredient, IngredientCategory

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Category.
    """
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'is_active', 'created_at', 'updated_at', 'company')
        read_only_fields = ('id', 'created_at', 'updated_at')

class IngredientCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientCategory
        fields = ('id', 'name', 'description')

class IngredientSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Ingredient.
    """
    category = IngredientCategorySerializer(read_only=True)
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'price', 'category']

class ProductIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)

    class Meta:
        model = ProductIngredient
        fields = ['id', 'ingredient', 'is_required', 'max_quantity']

class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Product.
    Inclui informações da categoria e ingredientes disponíveis.
    """
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        source='category'
    )
    available_ingredients = ProductIngredientSerializer(many=True, read_only=True, source='ingredients')
    company = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'category', 'category_id', 'name',
                 'description', 'price', 'image', 'is_active',
                 'available_ingredients', 'company',
                 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def to_representation(self, instance):
        """
        Sobrescreve o método para garantir que os ingredientes sejam retornados corretamente.
        """
        representation = super().to_representation(instance)
        # Garante que available_ingredients seja uma lista vazia se não houver ingredientes
        if not representation.get('available_ingredients'):
            representation['available_ingredients'] = []
        return representation

class ProductDetailSerializer(ProductSerializer):
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields

    def get_total_orders(self, obj):
        """
        Retorna o total de pedidos que incluem este produto.
        """
        return obj.orderitem_set.count()

    def get_total_revenue(self, obj):
        """
        Retorna a receita total gerada por este produto.
        """
        return sum(item.unit_price * item.quantity for item in obj.orderitem_set.all()) 