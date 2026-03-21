from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import User, Portfolio, Asset
from .serializers import UserSerializer, PortfolioSerializer, AssetSerializer
from .forms import LoginForm, UserRegistrationForm

# Usuário 

class UserLoginView(LoginView):
    template_name = "login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True # evita que usuários logados vejam o login novamente
    next_page = reverse_lazy("portfolio-create")  # Redireciona para criar portfólio após login

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


# Portfolio 

class PortfolioCreateView(generics.CreateAPIView):
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class UserPortfolioListView(generics.ListAPIView):
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.portfolios.all()


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

class AssetCreateView(generics.CreateAPIView):
    """
    Criar um novo asset em um portfólio.
    Valida com a BRAPI API automaticamente.
    """
    serializer_class = AssetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class PortfolioAssetListView(generics.ListAPIView):
    """
    Listar todos os assets de um portfólio específico.
    """
    serializer_class = AssetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        portfolio_id = self.kwargs.get('portfolio_id')
        user = self.request.user
        
        # Garantir que o portfólio pertence ao usuário
        return Asset.objects.filter(
            portfolio__id=portfolio_id,
            portfolio__user=user
        )


class AssetDeleteView(generics.DestroyAPIView):
    """Deletar um asset específico"""
    serializer_class = AssetSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        return Asset.objects.filter(portfolio__user=user)