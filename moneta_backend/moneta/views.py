from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .forms import LoginForm, UserRegistrationForm
from .models import User
from .serializers import UserSerializer


class UserLoginView(LoginView):
    template_name = "login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    pass


def register_view(request):
    if request.user.is_authenticated:
        return redirect("web-user-list")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Conta criada com sucesso. Agora faça login.")
            return redirect("login")
    else:
        form = UserRegistrationForm()

    return render(request, "register.html", {"form": form})


@login_required
def user_list_view(request):
    users = User.objects.order_by("-date_joined")
    return render(request, "user_list.html", {"users": users, "is_paginated": False})

class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]