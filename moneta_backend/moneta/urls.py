from django.urls import path
from .views import (
    UserCreateAPIView,
    UserListAPIView,
    UserLoginView,
    UserLogoutView,
    register_view,
    user_list_view,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', user_list_view, name='web-user-list'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', register_view, name='register'),

    path('users/', UserCreateAPIView.as_view(), name='user-create'),
    path('users/list/', UserListAPIView.as_view(), name='user-list'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]