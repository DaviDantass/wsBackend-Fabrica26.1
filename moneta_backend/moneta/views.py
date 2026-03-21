from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import FormView
from rest_framework import generics, permissions
from .models import User, Portfolio
from .serializers import UserSerializer, PortfolioSerializer
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