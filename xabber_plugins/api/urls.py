from django.urls import path
from .views import PluginListApi

urlpatterns = [
    path('plugins/', PluginListApi.as_view(), name='plugins'),
]
