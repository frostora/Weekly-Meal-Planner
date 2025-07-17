# this script is to edit meals and ingredients from the database

from .models import Meal, Ingredient

def save_changes(request, meal, Ingredient, meal_category, user):

    for ing_id in request.session["pending_additions"]:
        ingredient = Ingredient.objects.filter(id=ing_id, user=user).first()
        if ingredient:
            meal.ingredients.add(ingredient)

    for ing_id in request.session["pending_removals"]:
        ingredient = Ingredient.objects.filter(id=ing_id, user=user).first()
        if ingredient:
            meal.ingredients.remove(ingredient)

    meal.category = meal_category
    meal.user = user
    meal.save()

    # Clear after save
    request.session["pending_additions"] = []
    request.session["pending_removals"] = []
    
    request.session.modified = True
        

def discard_changes(request):
    request.session["pending_additions"] = []
    request.session["pending_removals"] = []
    request.session.modified = True


def save_new_meal(request, meal, Ingredient, meal_name, meal_category, user):

    meal.portions = 1
    meal.user = user
    meal.name = meal_name
    meal.category = meal_category

    meal.save()

    ingredient_ids = request.session.get("pending_additions", [])
    ingredients = Ingredient.objects.filter(id__in=ingredient_ids, user=user)
    meal.ingredients.add(*ingredients)  # add all at once


    # Clear after save
    request.session["pending_additions"] = []
    request.session.modified = True

def delete_meal(meal_id, user):
    try:
        meal = Meal.objects.get(id=meal_id,user=user)
        meal.delete()
    except Meal.DoesNotExist:
        pass

def delete_ingredient(ing_id, user):
    try:
        ing = Ingredient.objects.get(id=ing_id, user=user)
        ing.delete()
    except Ingredient.DoesNotExist:
        pass


def save_new_ingredient(ingredient, ing_name, ing_portions, user):
    ingredient.portions = int(ing_portions) if ing_portions else 1
    ingredient.name = ing_name
    ingredient.user = user
    ingredient.save()