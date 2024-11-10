import csv
import re
import json
from fractions import Fraction
from random import Random

# List of common units
common_units = ['c', 'cup', 'cups', 'oz', 'ounce', 'ounces', 'tsp', 'teaspoon', 'tbsp', 'tablespoon', 'lb', 'pound',
                'g', 'gram', 'grams', 'ml', 'liters', 'pkg', 'package', 'container', 'jar', 'carton', 'can']


# Function to parse a quantity string that may contain fractions
def parse_quantity(quantity_str):
    try:
        # If quantity is a fraction like '1/2'
        if '/' in quantity_str:
            return float(Fraction(quantity_str))
        # If quantity is a decimal or whole number
        return float(quantity_str)
    except ValueError:
        return 1.0  # Default to 1 if unable to parse


# Function to parse each ingredient entry
def parse_ingredient(ingredient):
    parts = ingredient.lower().strip().split()

    quantity = 1.0  # default quantity
    unit = ""
    name = ""
    details = ""

    # Try to parse the first part as a quantity (could be a number or fraction)
    if parts:
        quantity = parse_quantity(parts[0])
        parts = parts[1:]  # Remove the quantity part

    # Check if the next part is a unit
    if parts and (parts[0] in common_units or parts[0].rstrip('.').replace('(', '').replace(')', '') in common_units):
        unit = parts[0]
        parts = parts[1:]  # Remove the unit part

    # Join remaining parts as the name, and look for details in parentheses
    name = ' '.join(parts)
    if '(' in name and ')' in name:
        # Extract content inside parentheses as details
        start = name.index('(')
        end = name.index(')')
        details = name[start + 1:end]
        name = name[:start].strip() + ' ' + name[end + 1:].strip()

    # Return structured ingredient information
    return {
        'quantity': quantity,
        'unit': unit,
        'name': name.strip(),
        'details': details.strip() if details else ""
    }


def read_old(filename="RecipeNLG_dataset.csv", new_csv="Recipes.csv"):
    with open(filename, mode="r") as f:
        reader = csv.DictReader(f)
        with open(new_csv, mode="w", newline="") as f2:
            writer = csv.writer(f2)
            # Write header to the new CSV file
            writer.writerow(["title", "ingredients"])

            i = 0
            for row in reader:
                writer.writerow(
                    [row['title'], row['ingredients']])  # Assuming 'ingredients' is a field in the original file
                i += 1
                if i >= 1000:
                    break

# Function to read recipes from a CSV file
def read_recipes(filename="Recipes.csv"):
    recipe_ingredients = {}
    with open(filename, mode="r") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            title = row['title']
            # Parse the JSON string of ingredients
            ingredients = json.loads(row['ingredients'])
            # Parse each ingredient into a structured dictionary with quantity, unit, and name
            parsed_ingredients = [parse_ingredient(ing) for ing in ingredients]
            recipe_ingredients[i] = {'title': title, 'ingredients': parsed_ingredients}
    return recipe_ingredients


# Function to check if a user's ingredient matches any part of the recipe's ingredient name
def is_ingredient_match(user_ingredient, recipe_ingredient_name):
    user_ingredient = ' '.join(str(str(user_ingredient).lower().split('\n')[0]).split()[1:]).split("'")[0]
    recipe_ingredient_name = recipe_ingredient_name.lower().split()


    for i in user_ingredient:
        if i in recipe_ingredient_name:
            return True
    return False


# Function to find recipes with at least 60% match of ingredients
def find_recipes_with_ingredients(user_ingredients, filename="Recipes.csv", min_match=0.6):
    recipes = read_recipes(filename)  # Get the recipes
    matching_recipes = []

    # Parse and normalize user ingredients to only keep ingredient names
    #parsed_user_ingredients = [parse_ingredient(ing)['name'] for ing in user_ingredients]

    # Iterate through each recipe to count matching ingredients
    for recipe in recipes.values():
        recipe_title = recipe['title']
        recipe_ingredients = recipe['ingredients']

        # Count matches between user ingredients and recipe ingredients
        common_count = 0
        for user_ingredient in user_ingredients:
            for recipe_ingredient in recipe_ingredients:
                # Check if the user ingredient matches the recipe ingredient name
                if is_ingredient_match(user_ingredient[1], recipe_ingredient['name']):
                    common_count += 1
                    break

        # Calculate match percentage
        match_percentage = common_count / len(recipe_ingredients) if recipe_ingredients else 0
        if match_percentage >= min_match:
            matching_recipes.append({
                'title': recipe_title,
                'ingredients': recipe_ingredients  # Store the full ingredient details with measurements
            })

    return matching_recipes

stores = ['HEB', 'TARGET', 'WALMART']

def get_item_price(item):

    return Random().random()

def calculate_recipe_cost(recipe):
    prices = []
    for store in stores:
        cost = 0
        for item in recipe:
            cost += get_item_price(item)  # Assuming get_item_price uses the store context to fetch prices

        prices.append(cost)  # Store prices with the store names

    min = prices[0]

    for i in range(len(prices)):
        if prices[i] < min:
            min = prices[i]
    return min

# Example usage:
#read_old()  # Create Recipes.csv from the original file