# Generated by Django 4.2.21 on 2025-05-26 15:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_remove_productingredient_is_addable_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='company',
        ),
        migrations.RemoveField(
            model_name='product',
            name='company',
        ),
    ]
