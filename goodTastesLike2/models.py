from django.db import models
from django.contrib.auth.models import User
import os


# To handle images, we need a function to define the upload path
def recipe_image_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/recipe_images/<recipe_id>/<filename>
    return f'recipe_images/{instance.id}/{filename}'


class Tag(models.Model):
    """
    Model for a recipe tag (e.g., "spicy", "dessert", "quick").
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Main model for a Recipe. Based on the provided schema.
    """
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    prep_time = models.IntegerField(help_text="Preparation time in minutes")
    cook_time = models.IntegerField(help_text="Cooking time in minutes")
    servings = models.IntegerField(help_text="Number of servings")

    notes = models.TextField(blank=True, null=True, help_text="Optional notes, tips, or variations")
    image = models.ImageField(upload_to='recipe_images/', blank=True, null=True)

    tags = models.ManyToManyField(Tag, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Instruction(models.Model):
    """
    Model for a single instruction step, linked to a Recipe.
    """
    recipe = models.ForeignKey(Recipe, related_name='instructions', on_delete=models.CASCADE)
    step_number = models.PositiveIntegerField()
    description = models.TextField()

    class Meta:
        # Ensure steps are ordered correctly for each recipe
        ordering = ['step_number']
        unique_together = ('recipe', 'step_number')

    def __str__(self):
        return f'{self.recipe.name} - Step {self.step_number}'


class Ingredient(models.Model):
    """
    Model for a single ingredient, linked to a Recipe.
    """
    # Unit choices based on the schema's enum
    UNIT_CHOICES = [
        ('cup', 'cup(s)'),
        ('tsp', 'teaspoon(s)'),
        ('Tbsp', 'tablespoon(s)'),
        ('oz', 'ounce(s)'),
        ('g', 'gram(s)'),
        ('kg', 'kilogram(s)'),
        ('ml', 'milliliter(s)'),
        ('l', 'liter(s)'),
        ('qty', 'qty'),
        ('pinch', 'pinch'),
        ('to taste', 'to taste'),
    ]

    recipe = models.ForeignKey(Recipe, related_name='ingredients', on_delete=models.CASCADE)

    # Per the schema, ingredients are grouped (e.g., "wet", "dry", "garnish")
    group = models.CharField(max_length=100, default='Ingredients', help_text="Group (e.g., 'Wet', 'Dry', 'Garnish')")

    name = models.CharField(max_length=255)

    # Storing amount as CharField is most flexible for "1-2", "1.5", etc.
    amount = models.CharField(max_length=50)
    units = models.CharField(max_length=50, choices=UNIT_CHOICES)

    notes = models.CharField(max_length=255, blank=True, null=True,
                             help_text="Optional prep notes (e.g., 'chopped', 'melted')")

    def __str__(self):
        return f'{self.amount} {self.units} {self.name}'


