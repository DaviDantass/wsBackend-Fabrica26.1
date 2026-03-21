from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .forms import LoginForm, UserRegistrationForm
from .models import User
from .serializers import UserSerializer

class UserLoginView(LoginView):
    template_name = "login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True
    next_page = reverse_lazy("web-user-list")  

class UserLogoutView(LogoutView):
    next_page = reverse_lazy("login")  

class UserRegisterView(FormView):
    template_name = "register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("web-user-list")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, f"Conta de {user.username} criada com sucesso. Agora faça login.")
        return super().form_valid(form)

class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "user_list.html"
    context_object_name = "users"
    ordering = ["-date_joined"]
    paginate_by = 20  # página de 20 usuários
    login_url = reverse_lazy("login")


class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
