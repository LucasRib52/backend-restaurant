from django.db import models
from orders.models import Order

class ClientOrder(models.Model):
    """
    Modelo para pedidos feitos por clientes.
    Este modelo é uma cópia do Order mas sem autenticação.
    """
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='client_order')
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    customer_address = models.TextField()
    notes = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido #{self.order.id} - {self.customer_name}"

    class Meta:
        ordering = ['-created_at']
