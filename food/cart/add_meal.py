# This manages the scripts to add a meal to the list
# it will calculate ingredients, the cart, and the extras

from django.shortcuts import redirect
from .models import Meal

def reset_meals(request):
    request.session["selected_meals"] = []
    request.session.modified = True
    return redirect('index')

def get_id(slot_id, string):
    if string == "add":
        id, meal_type = slot_id.split("_")
        meal_id = None
    else:
        id, meal_type, meal_id = slot_id.split("_")

    id = int(id)

    if meal_type == "dinner":
        id += 7
        
    return id, meal_id

def add_meal(request, current_ids, meal_id ,slot_id):
    id, _ = get_id(slot_id, "add")

    if len(current_ids) <= id:
        current_ids.extend([[] for _ in range(id - len(current_ids) + 1)])
    
    if current_ids[id] is None:
        current_ids[id] = []

    if not isinstance(current_ids[id], list):
        current_ids[id] = [current_ids[id]]
    
    current_ids[id].append(meal_id)

    request.session["selected_meals"] = current_ids
    request.session.modified = True

def remove_meal(request, current_ids, slot_id):
    id, meal_id = get_id(slot_id, "remove")
    
    if not isinstance(current_ids[id], list):
        current_ids[id] = [current_ids[id]]

    if id < len(current_ids) and meal_id in current_ids[id]:
        current_ids[id].remove(meal_id)
        
    request.session["selected_meals"] = current_ids
    request.session.modified = True


def count_meals_and_ingredients(current_ids, selected_meals, ingredients, user):
    # this loop is to create 2 dictionaries, 
    # - one is meal_name, quantity
    # - the other is ingredient, quantity
    # all by summing the meals chosen
    for slot in current_ids:
        if not slot:
            continue
        for meal_id in slot:
            if meal_id is None:
                continue # skip placeholders
            
            meal = Meal.objects.filter(pk=meal_id, user=user).first()
            if not meal:
                slot.remove(meal_id)
                continue
        
            if meal in selected_meals:
                selected_meals[meal] += 1
            else:
                selected_meals[meal] = 1

            for ing in meal.ingredients.all():
                if ing in ingredients:
                    ingredients[ing] += 1
                else:
                    ingredients[ing] = 1

    # return the updated lists
    return selected_meals, dict(sorted(ingredients.items(), key=lambda item: item[0].name)), current_ids


def fill_cart(cart, ingredients):
    # in this loop we get the actual items we need to buy from the ingredients
    # for instance if we want 5 portions of pasta, we will
    # buy 1 box of pasta

    # we also create a list with the extra objects 
    extra_ingredients = []

    for _ in ingredients:
        # we calculate how many of that we need to buy
        if ingredients[_] % _.portions == 0:
            remainder = 0 
        else:
            remainder = 1
            extra_ingredients.append(_) 
        # if we have a remainder, we need a portion extra
        # for instance if I need 9 of pasta, 1 box is for 8 portions, 
        # i need 2 boxes

        n_to_buy = ingredients[_] // _.portions + remainder
        extra_portions = n_to_buy * _.portions - ingredients[_] 

        # we add the value to the dictionary
        cart[_] = {
            "to_buy": n_to_buy,
            "extra": extra_portions
            }
        
    return cart, extra_ingredients