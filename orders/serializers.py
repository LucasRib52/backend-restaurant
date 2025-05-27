from rest_framework import serializers
from .models import Order, OrderItem, OrderItemIngredient
from products.serializers import ProductSerializer, IngredientSerializer
from products.models import Product, Ingredient

class OrderItemIngredientSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo OrderItemIngredient.
    Inclui informações do ingrediente relacionado.
    """
    ingredient = IngredientSerializer(read_only=True)
    ingredient_id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        write_only=True,
        source='ingredient'
    )

    class Meta:
        model = OrderItemIngredient
        fields = ('id', 'order_item', 'ingredient', 'ingredient_id',
                 'is_added', 'price', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo OrderItem.
    Inclui informações do produto e ingredientes personalizados.
    """
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
        source='product'
    )
    product_name = serializers.CharField(read_only=True)
    ingredients = OrderItemIngredientSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'order', 'product', 'product_id', 'product_name', 'quantity',
                 'unit_price', 'notes', 'ingredients', 'total_price',
                 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_total_price(self, obj):
        """
        Calcula o preço total do item incluindo ingredientes personalizados.
        """
        base_price = obj.unit_price * obj.quantity
        ingredients_price = sum(ing.price for ing in obj.ingredients.all())
        return base_price + ingredients_price

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Order.
    Inclui informações dos itens do pedido.
    """
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.SerializerMethodField()
    customer_phone = serializers.SerializerMethodField()
    customer_address = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'customer_name', 'customer_phone', 'customer_address', 'status', 'status_display', 'total_amount',
                 'notes', 'items', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_customer_name(self, obj):
        if hasattr(obj, 'client_order'):
            return obj.client_order.customer_name
        return None

    def get_customer_phone(self, obj):
        if hasattr(obj, 'client_order'):
            return obj.client_order.customer_phone
        return None

    def get_customer_address(self, obj):
        if hasattr(obj, 'client_order'):
            return obj.client_order.customer_address
        return None

class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criar um novo pedido.
    Inclui validações e cálculos automáticos.
    """
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )

    class Meta:
        model = Order
        fields = ('customer_name', 'customer_phone', 'customer_address', 'notes', 'items', 'total_amount')
        read_only_fields = ('id', 'created_at', 'updated_at', 'status')

    def create(self, validated_data):
        """
        Cria um novo pedido com seus itens e ingredientes.
        """
        items_data = validated_data.pop('items')
        total_amount = validated_data.pop('total_amount', 0)
        
        order = Order.objects.create(
            **validated_data,
            total_amount=total_amount,
            status='pending'
        )
        
        for item_data in items_data:
            # Criar o item do pedido
            order_item = OrderItem.objects.create(
                order=order,
                product_name=item_data.get('product_name', 'Produto'),
                quantity=item_data.get('quantity', 1),
                unit_price=item_data.get('unit_price', 0),
                notes=item_data.get('notes', '')
            )
            
            # Adicionar ingredientes se houver
            if 'ingredients' in item_data:
                for ingredient_data in item_data['ingredients']:
                    try:
                        ingrediente = Ingredient.objects.get(id=ingredient_data['ingredient'])
                        OrderItemIngredient.objects.create(
                            order_item=order_item,
                            ingredient=ingrediente,
                            is_added=ingredient_data.get('is_added', True),
                            price=ingredient_data.get('price', ingrediente.price or 0)
                        )
                    except Ingredient.DoesNotExist:
                        continue
        
        return order

class OrderUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para atualizar o status de um pedido.
    """
    class Meta:
        model = Order
        fields = ('status', 'notes') 