from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.postgres.fields import ArrayField
import json


class Recipe(models.Model):
    """Main Recipe model based on the JSON schema"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    prep_time = models.IntegerField(validators=[MinValueValidator(0)], help_text="Preparation time in minutes")
    cook_time = models.IntegerField(validators=[MinValueValidator(0)], help_text="Cooking time in minutes")
    servings = models.IntegerField(validators=[MinValueValidator(1)])
    notes = models.TextField(blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_time(self):
        return self.prep_time + self.cook_time


class Tag(models.Model):
    """Tags for categorizing recipes"""
    name = models.CharField(max_length=50, unique=True)
    recipes = models.ManyToManyField(Recipe, related_name='tags', blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient model"""
    UNIT_CHOICES = [
        ('cup', 'Cup'),
        ('cups', 'Cups'),
        ('tsp', 'Teaspoon'),
        ('teaspoon', 'Teaspoon'),
        ('teaspoons', 'Teaspoons'),
        ('Tbs', 'Tablespoon'),
        ('Tbsp', 'Tablespoon'),
        ('tablespoon', 'Tablespoon'),
        ('tablespoons', 'Tablespoons'),
        ('oz', 'Ounce'),
        ('ounce', 'Ounce'),
        ('ounces', 'Ounces'),
        ('g', 'Gram'),
        ('gram', 'Gram'),
        ('grams', 'Grams'),
        ('kg', 'Kilogram'),
        ('kilogram', 'Kilogram'),
        ('kilograms', 'Kilograms'),
        ('ml', 'Milliliter'),
        ('milliliter', 'Milliliter'),
        ('milliliters', 'Milliliters'),
        ('l', 'Liter'),
        ('liter', 'Liter'),
        ('liters', 'Liters'),
        ('qty', 'Quantity'),
        ('pinch', 'Pinch'),
        ('to taste', 'To Taste'),
    ]

    GROUP_CHOICES = [
        ('wet', 'Wet'),
        ('dry', 'Dry'),
        ('other', 'Other'),
    ]

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=200)
    amount = models.CharField(max_length=50)  # Store as string to handle ranges like "1-2"
    units = models.CharField(max_length=20, choices=UNIT_CHOICES)
    notes = models.CharField(max_length=255, blank=True, null=True)
    group = models.CharField(max_length=20, choices=GROUP_CHOICES, default='other')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['group', 'order']

    def __str__(self):
        return f"{self.amount} {self.units} {self.name}"


class Instruction(models.Model):
    """Recipe instruction/step model"""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='instructions')
    step_number = models.IntegerField(validators=[MinValueValidator(1)])
    description = models.TextField()

    class Meta:
        ordering = ['step_number']
        unique_together = ['recipe', 'step_number']

    def __str__(self):
        return f"Step {self.step_number}: {self.description[:50]}"