from django.db import models
from django.utils.text import slugify
from django.db.models import JSONField
from django.core.exceptions import ValidationError
from datetime import datetime, time

class OpeningHour(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Segunda'),
        (1, 'Terça'),
        (2, 'Quarta'),
        (3, 'Quinta'),
        (4, 'Sexta'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    settings = models.ForeignKey('Settings', on_delete=models.CASCADE, related_name='opening_hours')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_open = models.BooleanField(default=True)
    is_holiday = models.BooleanField(default=False)
    next_day_closing = models.BooleanField(default=False, help_text='Indica se o fechamento é no dia seguinte')

    class Meta:
        unique_together = ('settings', 'day_of_week', 'is_holiday')
        verbose_name = 'Horário de Funcionamento'
        verbose_name_plural = 'Horários de Funcionamento'

    def __str__(self):
        return f"{self.get_day_of_week_display()} - {'Feriado' if self.is_holiday else 'Normal'}"

    def clean(self):
        if self.opening_time and self.closing_time:
            # Se o horário de fechamento for menor que o de abertura, 
            # automaticamente marca como fechamento no dia seguinte
            if self.closing_time < self.opening_time:
                self.next_day_closing = True

    def is_currently_open(self):
        """
        Verifica se o restaurante está aberto no momento atual
        """
        now = datetime.now().time()
        current_day = datetime.now().weekday()

        # Se não estiver aberto hoje, retorna False
        if not self.is_open or self.day_of_week != current_day:
            return False

        # Se o fechamento é no dia seguinte
        if self.next_day_closing:
            return now >= self.opening_time or now <= self.closing_time
        
        # Se o fechamento é no mesmo dia
        return self.opening_time <= now <= self.closing_time

class Settings(models.Model):
    """
    Modelo que representa as configurações do sistema.
    """
    business_name = models.CharField(max_length=100, verbose_name='Nome do Negócio')
    business_phone = models.CharField(max_length=20, verbose_name='Telefone')
    business_address = models.CharField(max_length=200, verbose_name='Endereço')
    business_email = models.EmailField(verbose_name='E-mail')
    business_photo = models.ImageField(upload_to='restaurant_photos/', null=True, blank=True, verbose_name='Foto do Restaurante')
    business_slug = models.SlugField(max_length=100, unique=True, null=True, blank=True, verbose_name='Link Personalizado')
    opening_time = models.TimeField(verbose_name='Horário de Abertura')
    closing_time = models.TimeField(verbose_name='Horário de Fechamento')
    is_open = models.BooleanField(default=True, verbose_name='Aberto')
    delivery_available = models.BooleanField(default=True, verbose_name='Delivery Disponível')
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Taxa de Entrega')
    minimum_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Pedido Mínimo')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Taxa de Imposto (%)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_methods = JSONField(default=dict, blank=True, null=True, verbose_name='Formas de Pagamento')

    class Meta:
        verbose_name = 'Configuração'
        verbose_name_plural = 'Configurações'

    def __str__(self):
        return self.business_name

    def save(self, *args, **kwargs):
        if not self.business_slug and self.business_name:
            self.business_slug = slugify(self.business_name)
        super().save(*args, **kwargs)
