from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout, get_user_model
from .models import User
from .serializers import (
    UserSerializer, UserCreateSerializer
)
from products.models import Category, Product
from products.serializers import CategorySerializer, ProductSerializer
import logging

# Configuração do logger
logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar usuários.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """
        Retorna o serializer apropriado baseado na ação.
        """
        if self.action == 'register':
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        """
        Retorna apenas o usuário atual.
        """
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """
        Endpoint para registro de novos usuários.
        """
        logger.info(f"Tentativa de registro com dados: {request.data}")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                logger.info(f"Usuário registrado com sucesso: {user.username}")
                
                # Faz login automático após o registro
                login(request, user)
                
                return Response({
                    'user': UserSerializer(user).data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Erro ao criar usuário: {str(e)}")
                return Response(
                    {'error': f'Erro ao criar usuário: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        logger.error(f"Erros de validação no registro: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        """
        Endpoint para autenticação de usuários.
        """
        username = request.data.get('username')
        password = request.data.get('password')

        logger.info(f"Tentativa de login para usuário: {username}")

        if not username or not password:
            logger.warning("Tentativa de login sem username ou password")
            return Response(
                {'error': 'Por favor, forneça username e password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=username, password=password)

        if not user:
            logger.warning(f"Credenciais inválidas para usuário: {username}")
            return Response(
                {'error': 'Credenciais inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Faz login usando o sistema do Django
        login(request, user)
        logger.info(f"Login bem-sucedido para usuário: {username}")

        return Response({
            'user': UserSerializer(user).data
        })

    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        Endpoint para logout do usuário.
        """
        logger.info(f"Logout do usuário: {request.user.username}")
        logout(request)
        return Response({'message': 'Logout realizado com sucesso'})

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Retorna os dados do usuário atual.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def public_menu(self, request):
        company_slug = request.query_params.get('slug')
        if not company_slug:
            return Response(
                {'error': 'Slug da empresa não fornecido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        company = get_object_or_404(User, company_slug=company_slug)
        # Buscar categorias e produtos ativos dessa empresa
        categories = Category.objects.filter(company=company, is_active=True)
        categories_data = []
        for category in categories:
            products = Product.objects.filter(category=category, is_active=True)
            products_serialized = ProductSerializer(products, many=True).data
            categories_data.append({
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'products': products_serialized
            })
        data = {
            'company_name': company.company_name,
            'company_logo': request.build_absolute_uri(company.company_logo.url) if company.company_logo else None,
            'company_description': company.company_description,
            'categories': categories_data
        }
        return Response(data)
