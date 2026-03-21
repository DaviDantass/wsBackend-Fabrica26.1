from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Portfolio, Asset
from .serializers import UserSerializer, PortfolioSerializer, AssetSerializer
from .forms import LoginForm, UserRegistrationForm
from utils.brapi import fetch_brapi_data

# Usuário 

class UserLoginView(LoginView):
    template_name = "login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True # evita que usuários logados vejam o login novamente
    next_page = reverse_lazy("dashboard")  # Redireciona para dashboard após login

class UserLogoutView(LogoutView):
    next_page = reverse_lazy("login")


class UserRegisterView(FormView):
    template_name = "register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        user = form.save()
        messages.success(
            self.request,
            f"Conta de {user.username} criada com sucesso. Agora faça login."
        )
        return super().form_valid(form)


class UserCreateAPIView(generics.CreateAPIView):
    """Criar usuário via API REST"""
    queryset = User.objects.all()
    serializer_class = UserSerializer


class GetTokenView(generics.GenericAPIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Retorna tokens JWT para o usuário logado"""
        user = request.user
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


# Portfolio

class PortfolioListCreateView(generics.ListCreateAPIView):
    """
    GET  /portfolios/         - Listar portfólios do usuário
    POST /portfolios/         - Criar novo portfólio
    Body (POST): {"name": "Meu Portfólio"}
    """
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.portfolios.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def create(self, request, *args, **kwargs):
        # Validar que name foi fornecido
        if not request.data.get('name'):
            return Response(
                {'error': 'Campo "name" é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)


class PortfolioRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /portfolios/<id>/  - Obter detalhes de um portfólio
    PUT    /portfolios/<id>/  - Atualizar portfólio (nome)
    PATCH  /portfolios/<id>/  - Atualizar parcialmente
    DELETE /portfolios/<id>/  - Deletar um portfólio
    Body (PUT): {"name": "Novo Nome"}
    """
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return self.request.user.portfolios.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


# Web Views - Dashboard
class DashboardView(LoginRequiredMixin, TemplateView):
    """Página de dashboard para gerenciar portfólios"""
    template_name = 'dashboard.html'
    login_url = 'login'


class PortfolioDetailView(LoginRequiredMixin, TemplateView):
    """Página de detalhes do portfólio"""
    template_name = 'portfolio_detail.html'
    login_url = 'login'


# Assets

class PortfolioAssetListCreateView(generics.ListCreateAPIView):
    """
    GET  /portfolios/<portfolio_id>/assets/         - Listar assets
    POST /portfolios/<portfolio_id>/assets/         - Criar novo asset
    Body (POST): {"ticker": "PETR4", "quantity": 100, "purchase_price": 25.50}
    """
    serializer_class = AssetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        portfolio_id = self.kwargs.get('portfolio_id')
        user = self.request.user
        return Asset.objects.filter(
            portfolio__id=portfolio_id,
            portfolio__user=user
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        context['portfolio_id'] = self.kwargs.get('portfolio_id')
        return context


class AssetDeleteView(generics.DestroyAPIView):
    """
    DELETE /assets/<id>/     - Deletar um asset
    """
    serializer_class = AssetSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        return Asset.objects.filter(portfolio__user=user)


class AssetRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /assets/<id>/         - Obter detalhes de um asset
    PUT    /assets/<id>/         - Atualizar asset (quantidade, preço de compra)
    PATCH  /assets/<id>/         - Atualizar parcialmente
    DELETE /assets/<id>/         - Deletar um asset
    Body (PUT): {"quantity": 150, "purchase_price": 26.50}
    """
    serializer_class = AssetSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        return Asset.objects.filter(portfolio__user=user)


class AssetDetailsView(generics.GenericAPIView):
    """
    GET /assets/details/<ticker>/  - Pegar dados da BRAPI para um ticker
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, ticker):
        try:
            data = fetch_brapi_data(ticker)
            return Response(data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )