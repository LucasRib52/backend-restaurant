# Generated by Django 4.2.10 on 2025-06-02 22:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_alter_promotion_reward_type_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='promotioningredient',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='promotioningredient',
            name='ingredient',
        ),
        migrations.RemoveField(
            model_name='promotioningredient',
            name='promotion',
        ),
        migrations.AlterUniqueTogether(
            name='promotionprogress',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='promotionprogress',
            name='promotion',
        ),
        migrations.DeleteModel(
            name='Promotion',
        ),
        migrations.DeleteModel(
            name='PromotionIngredient',
        ),
        migrations.DeleteModel(
            name='PromotionProgress',
        ),
    ]
