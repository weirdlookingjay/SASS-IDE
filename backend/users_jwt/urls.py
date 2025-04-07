from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginView, UserMeView, UserDetailView

urlpatterns = [
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserMeView.as_view(), name='user_me'),
    path('users/<str:username>/', UserDetailView.as_view(), name='user_detail'),
]
