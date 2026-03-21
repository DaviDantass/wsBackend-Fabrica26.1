from django.urls import path
from django.urls import path
from .views import PortfolioCreateView

from .views import (
    UserCreateAPIView,
    UserLoginView,
    UserLogoutView,
    UserRegisterView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', UserRegisterView.as_view(), name='register'),

    path('users/', UserCreateAPIView.as_view(), name='user-create'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('portfolios/create/', PortfolioCreateView.as_view(), name='portfolio-create'),
    
