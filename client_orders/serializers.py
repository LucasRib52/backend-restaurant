from rest_framework import serializers
from .models import ClientOrder
from orders.models import Order, OrderItem, OrderItemIngredient
from products.models import Ingredient

class ClientOrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criar um novo pedido de cliente.
    """
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    payment_method = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    change_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)

    class Meta:
        model = ClientOrder
        fields = ('customer_name', 'customer_phone', 'customer_address', 'notes', 'items', 'total_amount', 'payment_method', 'change_amount')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def create(self, validated_data):
        """
        Cria um novo pedido com seus itens e ingredientes.
        """
        items_data = validated_data.pop('items')
        total_amount = validated_data.pop('total_amount', 0)
        payment_method = validated_data.pop('payment_method', None)
        change_amount = validated_data.pop('change_amount', None)
        
        # Criar o pedido principal
        order = Order.objects.create(
            status='pending',
            total_amount=total_amount,
            payment_method=payment_method,
            change_amount=change_amount
        )
        
        # Criar o pedido do cliente
        client_order = ClientOrder.objects.create(
            order=order,
            total_amount=total_amount,
            payment_method=payment_method,
            change_amount=change_amount,
            **validated_data
        )
        
        # Criar os itens do pedido
        for item_data in items_data:
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
        
        return client_order 