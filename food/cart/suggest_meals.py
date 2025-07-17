# This script is for suggesting meals based on the extras
# considering best fits, 1 or 2 missing ingredients

from .models import Meal

max_missing = 2 # how many ingredients can be missing to still suggest that meal

def suggest_possible_meal(extras, user):
    meals = Meal.objects.filter(user=user)

    suggestions= {
        "best_fit": [],
        "partial_fit": []
    }

    for m in meals:
        extra_ids = [e.id for e in extras]
        needed_ingredients = [i for i in m.ingredients.all() if i.id not in extra_ids]
        
        # we now check if we can suggest this meal
        # if we have a best fit
        if len(needed_ingredients) == 0:
            suggestions["best_fit"].append(m)
        elif len(needed_ingredients) <= max_missing:
        # if we miss just a few ingredients
            suggestions["partial_fit"].append((m, needed_ingredients))
    
    suggestions["partial_fit"].sort(key=lambda pair: len(pair[1]))
    return suggestions