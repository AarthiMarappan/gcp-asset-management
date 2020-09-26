from django.urls import path
from . import views

urlpatterns = [
    path('', views.AssetView.create),
    path('<int:id>', views.AssetView.get),
]