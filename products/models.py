from django.db import models
from accounts.models import User
from django.core.validators import MinValueValidator

class Category(models.Model):
    """
    Modelo que representa uma categoria de produtos.
    """
    name = models.CharField(max_length=100, verbose_name='Nome')
    description = models.TextField(blank=True, verbose_name='Descrição')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    company = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories', null=True, blank=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    """
    Modelo que representa um produto.
    """
    name = models.CharField(max_length=100, verbose_name='Nome')
    description = models.TextField(verbose_name='Descrição')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço')
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Imagem')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Categoria')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    company = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products', null=True, blank=True)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['name']

    def __str__(self):
        return self.name

class IngredientCategory(models.Model):
    """
    Modelo que representa uma subcategoria de ingredientes (ex: Molhos, Proteínas, etc).
    """
    name = models.CharField(max_length=100, verbose_name='Nome da Subcategoria')
    description = models.TextField(blank=True, verbose_name='Descrição')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Subcategoria de Ingrediente'
        verbose_name_plural = 'Subcategorias de Ingredientes'
        ordering = ['name']

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    """
    Modelo que representa um ingrediente.
    """
    name = models.CharField(max_length=100, verbose_name='Nome')
    description = models.TextField(blank=True, verbose_name='Descrição')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Preço')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    category = models.ForeignKey(IngredientCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='ingredients', verbose_name='Subcategoria')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ingrediente'
        verbose_name_plural = 'Ingredientes'
        ordering = ['name']

    def __str__(self):
        return self.name

class ProductIngredient(models.Model):
    """
    Modelo que relaciona produtos com ingredientes.
    Permite definir quais ingredientes podem ser adicionados/removidos de cada produto.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    is_required = models.BooleanField(default=False)
    max_quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ingrediente do Produto'
        verbose_name_plural = 'Ingredientes dos Produtos'
        unique_together = ['product', 'ingredient']

    def __str__(self):
        return f"{self.product.name} - {self.ingredient.name}"
