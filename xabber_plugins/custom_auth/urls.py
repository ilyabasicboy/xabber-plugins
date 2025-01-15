from django.urls import path
from .views import DeveloperLoginView, DeveloperLogoutView

urlpatterns = [
    path('login/', DeveloperLoginView.as_view(), name='login'),
    path('logout/', DeveloperLogoutView.as_view(), name='logout'),
]
