from django.shortcuts import render, get_object_or_404
from .models import Recipe


def home(request):
    """
    View for the homepage - displays recipe cards with summary info.
    """
    recipes = Recipe.objects.all().prefetch_related('tags').order_by('-created_at')

    context = {
        'recipes': recipes
    }
    return render(request, 'goodTastesLike2/home.html', context)


def recipe_detail(request, recipe_id):
    """
    View for individual recipe detail page with portion calculator.
    """
    recipe = get_object_or_404(
        Recipe.objects.prefetch_related('ingredients', 'instructions', 'tags'),
        pk=recipe_id
    )

    context = {
        'recipe': recipe
    }
    return render(request, 'goodTastesLike2/recipe_detail.html', context)
