from django.contrib import admin
from .models import Recipe, Tag, Instruction, Ingredient


# These "Inline" classes allow us to edit Ingredients and Instructions
# directly on the Recipe admin page. It's much more user-friendly.

class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1  # Show 1 extra empty form by default
    fields = ('group', 'name', 'amount', 'units', 'notes')


class InstructionInline(admin.StackedInline):
    model = Instruction
    extra = 1  # Show 1 extra empty form by default
    fields = ('step_number', 'description')
    ordering = ('step_number',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'prep_time', 'cook_time', 'servings', 'updated_at')
    list_filter = ('author', 'tags')
    search_fields = ('name', 'description')

    # Add the inlines to the Recipe admin page
    inlines = [IngredientInline, InstructionInline]

    # Use a filter for the ManyToManyField
    filter_horizontal = ('tags',)

    # Auto-populate author field if not set
    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# We don't need to register Ingredient and Instruction separately,
# as they are now handled "inline" with the Recipe.
from django.contrib import admin

# Register your models here.
