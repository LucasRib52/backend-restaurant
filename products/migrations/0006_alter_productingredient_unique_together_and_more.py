# Generated by Django 4.2.21 on 2025-05-29 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_remove_category_company_remove_product_company'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='productingredient',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='productingredient',
            name='group_name',
            field=models.CharField(default='Sem Grupo', max_length=100, verbose_name='Grupo do Produto'),
        ),
    ]
