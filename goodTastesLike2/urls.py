from django.urls import path
from . import views

# This maps the app's root URL (which will be '' relative to the project)
# to the 'home' view.
urlpatterns = [
    path('', views.home, name='home'),
]
