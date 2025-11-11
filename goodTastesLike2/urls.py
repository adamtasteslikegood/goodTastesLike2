from django.urls import path
from . import views

app_name = 'goodTastesLike2'

urlpatterns = [
    path('', views.home, name='home'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
]
