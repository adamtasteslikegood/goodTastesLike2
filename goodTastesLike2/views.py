from django.shortcuts import render
from .models import Recipe


def home(request):
    """
    View for the homepage.
    Fetches all recipes and renders them in the home.html template.

    We use prefetch_related to efficiently grab all related
    ingredients and instructions in a minimal number of database queries.
    """
    recipes = Recipe.objects.all().prefetch_related('ingredients', 'instructions').order_by('-created_at')

    context = {
        'recipes': recipes
    }
    return render(request, 'goodTastesLike2/home.html', context)


from django.shortcuts import render

# Create your views here.
