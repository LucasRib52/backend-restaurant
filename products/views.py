from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from .models import Category, Product, Ingredient, ProductIngredient, IngredientCategory
from .serializers import (
    CategorySerializer, ProductSerializer,
    ProductDetailSerializer, IngredientSerializer,
    ProductIngredientSerializer
)
import json

# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de categorias.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.all()

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """
        Retorna todos os produtos de uma categoria específica.
        """
        category = self.get_object()
        products = Product.objects.filter(category=category)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de produtos.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_serializer_class(self):
        """
        Retorna o serializer apropriado baseado na ação.
        """
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer

    def get_queryset(self):
        """
        Retorna a lista de produtos ordenada por data de criação crescente.
        """
        queryset = Product.objects.all()
        category_id = self.request.query_params.get('category', None)
        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)
        return queryset

    def perform_create(self, serializer):
        """
        Cria um novo produto e seus ingredientes.
        """
        print("Iniciando criação do produto...")
        # Primeiro, salva o produto
        product = serializer.save()
        print(f"Produto criado: {product.name}")
        
        # Processa os ingredientes
        ingredients = []
        for key in self.request.data:
            if key.startswith('ingredients['):
                ingredients.append(self.request.data[key])
            
        print("Ingredientes recebidos:", ingredients)
        
        for ing_data in ingredients:
            try:
                # Tenta decodificar o JSON
                ing_obj = json.loads(ing_data)
                print("Processando ingrediente:", ing_obj)
                
                ing_name = ing_obj.get('name')
                cat_name = ing_obj.get('category')
                is_required = ing_obj.get('isRequired', False)
                max_quantity = ing_obj.get('maxQuantity', 1)
                
                if not ing_name:
                    print("Nome do ingrediente vazio, pulando...")
                    continue
                    
                # Cria ou obtém a categoria do grupo
                category = None
                if cat_name:
                    category, _ = IngredientCategory.objects.get_or_create(name=cat_name)
                    print(f"Categoria criada/encontrada: {category.name}")
                    
                # Cria ou obtém o ingrediente
                ingredient, _ = Ingredient.objects.get_or_create(
                    name=ing_name,
                    defaults={'category': category}
                )
                print(f"Ingrediente criado/encontrado: {ingredient.name}")
                
                # Se já existe mas não tem categoria, atualiza
                if ingredient.category != category:
                    ingredient.category = category
                    ingredient.save()
                    print(f"Categoria do ingrediente atualizada para: {category.name}")
                
                # Cria o novo ProductIngredient
                pi = ProductIngredient.objects.create(
                    product=product,
                    ingredient=ingredient,
                    group_name=cat_name,
                    is_required=bool(is_required),
                    max_quantity=int(max_quantity)
                )
                print(f"ProductIngredient criado: {pi}")
                
            except Exception as e:
                print(f"Erro ao processar ingrediente: {str(e)}")
                continue

    def perform_update(self, serializer):
        """
        Atualiza um produto existente e seus ingredientes.
        """
        print("Iniciando atualização do produto...")
        # Primeiro, salva as alterações do produto
        product = serializer.save()
        print(f"Produto salvo: {product.name}")
        
        # Processa os novos ingredientes
        ingredients = []
        for key in self.request.data:
            if key.startswith('ingredients['):
                ingredients.append(self.request.data[key])
        
        print(f"Total de ingredientes recebidos: {len(ingredients)}")
        
        if ingredients:  # Só remove e recria se houver novos ingredientes
            # Remove todos os ingredientes existentes
            ProductIngredient.objects.filter(product=product).delete()
            print("Ingredientes antigos removidos")
            
            for ing_data in ingredients:
                try:
                    # Tenta decodificar o JSON
                    ing_obj = json.loads(ing_data)
                    ing_name = ing_obj.get('name')
                    cat_name = ing_obj.get('category')
                    is_required = ing_obj.get('isRequired', False)
                    max_quantity = ing_obj.get('maxQuantity', 1)
                    
                    print(f"Processando ingrediente: {ing_name} (categoria: {cat_name})")
                    
                    if not ing_name:
                        print("Nome do ingrediente vazio, pulando...")
                        continue
                        
                    category = None
                    if cat_name:
                        category, _ = IngredientCategory.objects.get_or_create(name=cat_name)
                        print(f"Categoria criada/encontrada: {category.name}")
                        
                    ingredient, _ = Ingredient.objects.get_or_create(
                        name=ing_name,
                        defaults={'category': category}
                    )
                    print(f"Ingrediente criado/encontrado: {ingredient.name}")
                    
                    # Se já existe mas não tem categoria, atualiza
                    if ingredient.category != category:
                        ingredient.category = category
                        ingredient.save()
                        print(f"Categoria do ingrediente atualizada para: {category.name}")
                    
                    # Cria o novo ProductIngredient
                    pi = ProductIngredient.objects.create(
                        product=product,
                        ingredient=ingredient,
                        group_name=cat_name,
                        is_required=bool(is_required),
                        max_quantity=int(max_quantity)
                    )
                    print(f"ProductIngredient criado: {pi}")
                    
                except Exception as e:
                    print(f"Erro ao processar ingrediente: {str(e)}")
                    continue
        else:
            print("Nenhum ingrediente recebido, mantendo os existentes")

    @action(detail=True, methods=['post'])
    def add_ingredient(self, request, pk=None):
        """
        Adiciona um ingrediente a um produto.
        """
        product = self.get_object()
        ingredient_id = request.data.get('ingredient_id')
        is_removable = request.data.get('is_removable', False)
        is_addable = request.data.get('is_addable', True)

        try:
            ingredient = Ingredient.objects.get(
                id=ingredient_id
            )
        except Ingredient.DoesNotExist:
            return Response(
                {'error': 'Ingrediente não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        product_ingredient, created = ProductIngredient.objects.get_or_create(
            product=product,
            ingredient=ingredient,
            defaults={
                'is_removable': is_removable,
                'is_addable': is_addable
            }
        )

        if not created:
            product_ingredient.is_removable = is_removable
            product_ingredient.is_addable = is_addable
            product_ingredient.save()

        serializer = ProductIngredientSerializer(product_ingredient)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def remove_ingredient(self, request, pk=None):
        """
        Remove um ingrediente de um produto.
        """
        product = self.get_object()
        ingredient_id = request.data.get('ingredient_id')

        try:
            ingredient = Ingredient.objects.get(
                id=ingredient_id
            )
        except Ingredient.DoesNotExist:
            return Response(
                {'error': 'Ingrediente não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            product_ingredient = ProductIngredient.objects.get(
                product=product,
                ingredient=ingredient
            )
            product_ingredient.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProductIngredient.DoesNotExist:
            return Response(
                {'error': 'Ingrediente não encontrado no produto'},
                status=status.HTTP_404_NOT_FOUND
            )

class IngredientViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de ingredientes.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def get_queryset(self):
        return Ingredient.objects.all()

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Retorna todos os ingredientes disponíveis.
        """
        ingredients = Ingredient.objects.all()
        serializer = IngredientSerializer(ingredients, many=True)
        return Response(serializer.data)
