from django.urls import path
from xabber_plugins.plugins import views

urlpatterns = [
    path('', views.PluginListView.as_view(), name='plugin_list'),
    path('<str:plugin_name>/detail/', views.PluginDetail.as_view(), name='plugin_detail'),
    path('<str:plugin_name>/delete/', views.PluginDelete.as_view(), name='plugin_delete'),
    path('<str:plugin_name>/add_description/', views.AddPluginDescription.as_view(), name='add_description'),
    path('<str:plugin_name>/delete_description/<int:description_id>/', views.DeletePluginDescription.as_view(), name='delete_description'),
    path('<str:plugin_name>/release_create/', views.ReleaseCreate.as_view(), name='release_create'),
    path('<str:plugin_name>/release_delete/<int:release_id>/', views.ReleaseDelete.as_view(), name='release_delete')
]
