import json
import jsonschema
from django.core.management.base import BaseCommand
from goodTastesLike2.models import Recipe, Tag, Ingredient, Instruction


class Command(BaseCommand):
    help = 'Import recipes from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to JSON file containing recipes')
        parser.add_argument(
            '--no-validate',
            action='store_true',
            help='Skip schema validation'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing recipes before importing'
        )

    def handle(self, *args, **options):
        json_file = options['json_file']
        validate = not options['no_validate']
        clear = options['clear']

        if clear:
            self.stdout.write('Clearing existing recipes...')
            Recipe.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared all recipes'))

        try:
            with open(json_file, 'r') as f:
                json_data = json.load(f)

            # Handle both single recipe and an array of recipes
            recipes = json_data if isinstance(json_data, list) else [json_data]

            # Validate if requested
          
            # ... existing code ...
            # Validate against schema if requested
            if validate:
                import os
                from django.conf import settings
                schema_path = os.path.join(settings.BASE_DIR, 'recipe.schema.json')
                with open(schema_path, 'r') as schema_file:
                    schema = json.load(schema_file)
                # ... existing code ...
                
                for recipe_data in recipes:
                    jsonschema.validate(recipe_data, schema)
                self.stdout.write(self.style.SUCCESS('Schema validation passed'))

            # Import recipes
            imported_count = 0
            for recipe_data in recipes:
                recipe = self._create_recipe(recipe_data)
                imported_count += 1
                self.stdout.write(f'Imported: {recipe.name}')

            self.stdout.write(
                self.style.SUCCESS(f'Successfully imported {imported_count} recipe(s)')
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

    def _create_recipe(self, recipe_data):
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