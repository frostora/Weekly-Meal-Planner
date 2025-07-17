# ...

from .add_meal import count_meals_and_ingredients, fill_cart
from .suggest_meals import suggest_possible_meal
from .models import Meal

N_SLOTS = 14

def get_current_ids(request):
    # check if we already have a session. If not, initialise data
    if "selected_meals" not in request.session:
        # Initialize 14 slots (7 days, 2 slots per day), each as empty list
        request.session["selected_meals"] = [[] for _ in range(N_SLOTS)]

    return request.session["selected_meals"]


def make_meal_pairs(current_ids, user):
    while len(current_ids) < N_SLOTS:
        current_ids.append([])

    current_ids_int = [[safe_int(i) for i in slot] if slot is not None else [] for slot in current_ids]

    # for the weekly view I need to split them into pairs for lunch-dinner
    # Split meals into pairs (chunks of 2)
    # I need to go from objects to a list with couples of ids:
    flat_ids = [i for slot in current_ids_int for i in slot if i is not None]
    meals_qs = Meal.objects.filter(id__in=flat_ids, user=user)
    meal_dict = {meal.id: meal for meal in meals_qs}
    # But chunked_with_none expects a flat list of 14 meal ids (some may be None)
    # To generate that, flatten with placeholders for missing slots:

    # rebuild a flat list of length 14 with meal ids or None
    flat_14 = []
    for slot in current_ids_int:
        # slot is a list of meals in that slot, e.g. multiple meals
        if slot:
            flat_14.extend(slot)
        else:
            flat_14.append(None)

    # Make sure flat_14 has exactly 14 elements (N_SLOTS)
    while len(flat_14) < N_SLOTS:
        flat_14.append(None)

    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    week_meal_pairs = []
    for i in range(7):
        lunch_meals = [meal_dict.get(m_id) for m_id in current_ids_int[i] if m_id in meal_dict]
        dinner_meals = [meal_dict.get(m_id) for m_id in current_ids_int[i+7] if m_id in meal_dict]
        week_meal_pairs.append((weekdays[i], [lunch_meals, dinner_meals]))
        # this is a list of lists, each containing a list, in the form
    # [
    #   [[lunches_1], [dinners_1]],
    #   [[lunches_2 ], [dinners_2]],
    #   ...
    # ]
    return week_meal_pairs

def safe_int(id):
    try:
        return int(id)
    except (TypeError, ValueError):
        return None

def chunked_with_none(ids, meal_dict):
    result = []
    for i in range(7):  # 7 days
        lunch = meal_dict.get(ids[i]) if i < len(ids) else None
        dinner = meal_dict.get(ids[i+7]) if (i + 7) < len(ids) else None
        result.append([lunch, dinner])
    return result

def get_weekly_data(current_ids, category, user):

    ingredients = {} # for the total of ingredients, to calculate cart
    selected_meals = {} # to show the meals
    cart = {} # to see what needs to be bought
    extra_ingredients = [] # to keep track of what remains

    selected_meals, ingredients, current_ids = count_meals_and_ingredients(
        current_ids, selected_meals, ingredients, user
    )

    cart, extra_ingredients = fill_cart(cart, ingredients)
    
    # suggest meals
    suggestions = suggest_possible_meal(extra_ingredients, user)

    if category is not None:
        suggestions_filtered= {
            "best_fit": [],
            "partial_fit": []
        }
        suggestions_filtered["best_fit"] = [meal for meal in suggestions["best_fit"] if meal.category == category]
        suggestions_filtered["partial_fit"] = [meal_tuple for meal_tuple in suggestions["partial_fit"] if meal_tuple[0].category == category]
    else:
        suggestions_filtered = suggestions

    # to render things properly we send the meals in pairs, for lunch and dinner
    week_meal_pairs = make_meal_pairs(current_ids, user)
    

    # we return everything as a dictionary
    return {
        "ingredients": ingredients,
        "selected_meals": selected_meals,
        "cart": cart,
        "suggestions": suggestions_filtered,
        "week_meal_pairs": week_meal_pairs,
    }

from uuid import uuid4
from django.contrib.auth.models import User

def get_user(request):
    if request.user.is_authenticated:
        return request.user
    if not request.session.get('temp_user_id'):
        temp_user = User.objects.create(username=f'temp_{uuid4().hex[:10]}')
        request.session['temp_user_id'] = temp_user.id
    else:
        temp_user = User.objects.get(id=request.session['temp_user_id'])
    return temp_user
