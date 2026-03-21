from django.urls import path
from .views import (
    UserCreateAPIView,
    GetTokenView,
    UserLoginView,
    UserLogoutView,
    UserRegisterView,
    PortfolioListCreateView,
    PortfolioRetrieveUpdateDestroyView,
    DashboardView,
    PortfolioDetailView,
    PortfolioAssetListCreateView,
    AssetRetrieveUpdateDestroyView,
    AssetDetailsView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # REST API - RESTful design (com prefixo 'api/' para evitar conflitos)
    # Tokens (API)
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/session-token/', GetTokenView.as_view(), name='session-token'),

    # Users
    path('users/', UserCreateAPIView.as_view(), name='user-create'),

    # Portfolios
    path('portfolios/', PortfolioListCreateView.as_view(), name='portfolio-list-create'),
    path('portfolios/<int:id>/', PortfolioRetrieveUpdateDestroyView.as_view(), name='portfolio-retrieve-update-destroy'),

    # Assets under Portfolios
    path('portfolios/<int:portfolio_id>/assets/', PortfolioAssetListCreateView.as_view(), name='portfolio-asset-list-create'),
    path('assets/<int:id>/', AssetRetrieveUpdateDestroyView.as_view(), name='asset-retrieve-update-destroy'),
    path('assets/details/<str:ticker>/', AssetDetailsView.as_view(), name='asset-details'),

    # Autenticação (Web) - Ráiz é login
    path('', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', UserRegisterView.as_view(), name='register'),

    # Dashboard (Web)
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('portfolio/', PortfolioDetailView.as_view(), name='portfolio-detail'),
]