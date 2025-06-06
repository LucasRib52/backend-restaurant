# Generated by Django 4.2.21 on 2025-06-02 22:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_promotion_promotionreward_promotionitem'),
        ('orders', '0006_orderitem_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='item_type',
            field=models.CharField(choices=[('regular', 'Produto Regular'), ('promotion', 'Item de Promoção'), ('reward', 'Brinde de Promoção')], default='regular', max_length=20, verbose_name='Tipo do Item'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='promotion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_items', to='products.promotion'),
        ),
    ]
