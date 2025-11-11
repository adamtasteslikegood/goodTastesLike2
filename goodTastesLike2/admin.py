from django.contrib import admin
from django.contrib import messages
from django import forms
from django.urls import path
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
import json
import jsonschema
import requests
from pathlib import Path
from .models import Recipe, Tag, Ingredient, Instruction


class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1
    fields = ['group', 'name', 'amount', 'units', 'notes', 'order']
    ordering = ['group', 'order']


class InstructionInline(admin.TabularInline):
    model = Instruction
    extra = 1
    fields = ['step_number', 'description']
    ordering = ['step_number']


class TagInline(admin.TabularInline):
    model = Recipe.tags.through
    extra = 1


class JSONImportForm(forms.Form):
    json_file = forms.FileField(
        label='Select a JSON file',
        help_text='Upload a JSON file containing recipes following the schema',
        required=False,
        widget=forms.ClearableFileInput(attrs={'multiple': True})
    )
    json_path = forms.CharField(
        label='File path or URL',
        required=False,
        help_text='Import from a local file path or remote URL'
    )
    validate_schema = forms.BooleanField(
        label='Validate against schema',
        required=False,
        initial=True,
        help_text='Validate the JSON against the recipe schema before importing'
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'prep_time', 'cook_time', 'servings', 'created_at']
    list_filter = ['tags', 'created_at']
    search_fields = ['name', 'description']
    inlines = [IngredientInline, InstructionInline]
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Timing', {
            'fields': ('prep_time', 'cook_time', 'servings')
        }),
        ('Additional Info', {
            'fields': ('notes', 'image')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-json/', self.admin_site.admin_view(self.import_json_view), name='recipe_import_json'),
        ]
        return my_urls + urls

    def import_json_view(self, request):
        if request.method == 'POST':
            form = JSONImportForm(request.POST, request.FILES)
            if form.is_valid():
                validate = form.cleaned_data['validate_schema']
                json_path = form.cleaned_data.get('json_path', '').strip()

                all_recipes = []

                try:
                    # Handle file uploads (multiple files)
                    if request.FILES.getlist('json_file'):
                        for json_file in request.FILES.getlist('json_file'):
                            json_data = json.load(json_file)
                            recipes = json_data if isinstance(json_data, list) else [json_data]
                            all_recipes.extend(recipes)

                    # Handle path/URL input
                    elif json_path:
                        if json_path.startswith('http://') or json_path.startswith('https://'):
                            # Fetch from URL
                            response = requests.get(json_path, timeout=30)
                            response.raise_for_status()
                            json_data = response.json()
                        else:
                            # Read from local file path
                            file_path = Path(json_path)
                            if not file_path.exists():
                                raise FileNotFoundError(f'File not found: {json_path}')
                            with open(file_path, 'r') as f:
                                json_data = json.load(f)

                        recipes = json_data if isinstance(json_data, list) else [json_data]
                        all_recipes.extend(recipes)
                    else:
                        messages.error(request, 'Please select a file or enter a path/URL.')
                        return render(request, 'admin/recipe_import.html', {
                            'form': form,
                            'title': 'Import Recipes from JSON',
                            'site_header': self.admin_site.site_header,
                            'site_title': self.admin_site.site_title,
                            'has_permission': True,
                        })

                    # Validate against schema if requested
                    if validate:
                        import os
                        from django.conf import settings
                        schema_path = os.path.join(settings.BASE_DIR, 'recipe.schema.json')
                        with open(schema_path, 'r') as schema_file:
                            schema = json.load(schema_file)

                        for recipe_data in all_recipes:
                            jsonschema.validate(recipe_data, schema)

                    # Import recipes
                    imported_count = 0
                    for recipe_data in all_recipes:
                        recipe = self._create_recipe_from_json(recipe_data)
                        imported_count += 1

                    messages.success(
                        request,
                        f'Successfully imported {imported_count} recipe(s).'
                    )
                    return HttpResponseRedirect('/admin/goodTastesLike2/recipe/')

                except json.JSONDecodeError as e:
                    messages.error(request, f'Invalid JSON file: {e}')
                except jsonschema.ValidationError as e:
                    messages.error(request, f'Schema validation failed: {e.message}')
                except requests.RequestException as e:
                    messages.error(request, f'Error fetching URL: {str(e)}')
                except FileNotFoundError as e:
                    messages.error(request, str(e))
                except Exception as e:
                    messages.error(request, f'Error importing recipes: {str(e)}')
        else:
            form = JSONImportForm()

        context = {
            'form': form,
            'title': 'Import Recipes from JSON',
            'site_header': self.admin_site.site_header,
            'site_title': self.admin_site.site_title,
            'has_permission': True,
        }
        return render(request, 'admin/recipe_import.html', context)

    def _create_recipe_from_json(self, recipe_data):
        """Create a Recipe instance from JSON data"""
        # Create the main recipe
        recipe = Recipe.objects.create(
            name=recipe_data['name'],
            description=recipe_data.get('description', ''),
            prep_time=recipe_data['prepTime'],
            cook_time=recipe_data['cookTime'],
            servings=recipe_data['servings'],
            notes=recipe_data.get('notes', ''),
            image=recipe_data.get('image', '')
        )

        # Add ingredients
        ingredients_data = recipe_data.get('ingredients', {})
        order = 0
        for group, ingredients in ingredients_data.items():
            if group in ['wet', 'dry', 'other']:
                for ing_data in ingredients:
                    # Handle amount as either number or array
                    amount = ing_data['amount']
                    if isinstance(amount, list):
                        amount_str = f"{amount[0]}-{amount[1]}" if len(amount) == 2 else str(amount[0])
                    else:
                        amount_str = str(amount)

                    Ingredient.objects.create(
                        recipe=recipe,
                        name=ing_data['name'],
                        amount=amount_str,
                        units=ing_data['units'],
                        notes=ing_data.get('notes', ''),
                        group=group,
                        order=order
                    )
                    order += 1

        # Add instructions
        instructions = recipe_data.get('instructions', [])
        for i, instruction in enumerate(instructions, 1):
            if isinstance(instruction, str):
                Instruction.objects.create(
                    recipe=recipe,
                    step_number=i,
                    description=instruction
                )
            elif isinstance(instruction, dict):
                Instruction.objects.create(
                    recipe=recipe,
                    step_number=instruction.get('step', i),
                    description=instruction['description']
                )

        # Add tags
        tags = recipe_data.get('tags', [])
        for tag_name in tags:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            recipe.tags.add(tag)

        return recipe


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'recipe_count']
    search_fields = ['name']

    def recipe_count(self, obj):
        return obj.recipes.count()

    recipe_count.short_description = 'Number of Recipes'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'units', 'recipe', 'group']
    list_filter = ['group', 'units']
    search_fields = ['name', 'recipe__name']


@admin.register(Instruction)
class InstructionAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'step_number', 'description_preview']
    list_filter = ['recipe']
    search_fields = ['description', 'recipe__name']

    def description_preview(self, obj):
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description

    description_preview.short_description = 'Description'