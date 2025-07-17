from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Meal, Ingredient
from .add_meal import reset_meals, add_meal, remove_meal
from .edit import save_changes, discard_changes, save_new_meal, delete_meal, delete_ingredient,save_new_ingredient
from .functions import get_weekly_data, get_current_ids, get_user
from .network import send_email
from django.db.models.functions import Lower


def post_edit_meal(request, meal_id, editing, new_meal):
    form_type = request.POST.get("form_type")
    category = request.POST.get('category')
    user = get_user(request)

    if form_type == "delete_meal":
        delete_meal(meal_id, user)
        return redirect('edit-meals-view')

    if form_type == "choose_meal":
        discard_changes(request)
        return redirect('edit-specific-meal', meal_id=meal_id)
            

    if form_type == "add_ingredient":
        ingredient_name = request.POST.get("ingredient_name")

        if ingredient_name is not None:
            ingredient_obj = Ingredient.objects.filter(name=ingredient_name, user=user).first()
            ingredient_id = ingredient_obj.id
            if ingredient_id not in request.session["pending_additions"]:
                request.session["pending_additions"].append(ingredient_id) 
                request.session.modified = True

        if editing:
            return redirect('edit-specific-meal', meal_id)
        else: 
            return redirect('create-meal')
    
    elif form_type == "remove_ingredient":
        ingredient_name = request.POST.get("ingredient_name")
        ingredient_obj = Ingredient.objects.filter(name=ingredient_name, user=user).first() 
        ingredient_id = ingredient_obj.id
        
        # Remove from pending additions if present (added in current session)
        if ingredient_id in request.session.get("pending_additions", []):
            request.session["pending_additions"].remove(ingredient_id)
            request.session.modified = True 
            
        # Add to pending removals if not already there
        if ingredient_id not in request.session.get("pending_removals", []):
            request.session["pending_removals"].append(ingredient_id)
            request.session.modified = True 

        
        if editing:
            return redirect('edit-specific-meal', meal_id)
        else: 
            return redirect('create-meal')

    elif form_type == "save_new_changes":
        save_new_meal(request, new_meal, Ingredient, request.POST.get("meal_name"), category, user)
        return redirect('edit-meals-view')
    
    elif form_type == "save_changes":
        save_changes(request, Meal.objects.get(id=meal_id, user=user), Ingredient, category, user)
        return redirect('edit-meals-view')

    elif form_type == "discard_changes":
        discard_changes(request)
        return redirect('edit-meals-view')

    
    return redirect('edit-meals-view')


def post_edit_ingredient(request, ing_id, editing, new_ing):
    form_type = request.POST.get("form_type")
    user = get_user(request)
    if form_type == "delete_ingredient":
        delete_ingredient(ing_id, user)
        return redirect('edit-ingredients-view')

    if form_type == "choose_ingredient":
        return redirect('edit-specific-ingredient', ing_id)
            

    elif form_type == "save_new_ingredient":
        if editing:
            ingredient = Ingredient.objects.get(id=ing_id,user=user)
        else:
            ingredient = new_ing
        save_new_ingredient(ingredient, request.POST.get("ingredient_name"), request.POST.get("portion_count"), user)
        return redirect('edit-ingredients-view')
    
    elif form_type == "discard_changes":
        return redirect('edit-ingredients-view')

    
    return redirect('edit-ingredients-view')

def reset_pending(request):
    if "pending_additions" not in request.session:
        request.session["pending_additions"] = []

    if "pending_removals" not in request.session:
        request.session["pending_removals"] = []

def index(request):
    if request.method == "POST":
        if request.POST.get("form_type") == "reset":
            request.session["selected_meals"] = [[] for _ in range(14)]
    
    user = get_user(request)
    current_ids = get_current_ids(request)
    data = get_weekly_data(current_ids, None, user)
    week_meal_pairs = data["week_meal_pairs"]
    cart =  data["cart"]
    


    return render(request, "cart/index.html", {
        "week_meal_pairs": week_meal_pairs,
        "cart":cart
    })

def about(request):
    return render(request, "cart/about.html")

def contact(request):
    result = -1
    if request.method == "POST":
        if request.POST.get("form_type") == "contact":
            name = request.POST.get("name")
            email = request.POST.get("email")
            message = request.POST.get("message")
            result = send_email(name, email, message)
         
    return render(request, "cart/contact.html", {
        "result" : result # a boolean, if email sent was successful
    })

def edit_meal(request, meal_id = None):
    user = get_user(request)
    meal_id = request.POST.get("meal_id") or meal_id
    meal_id = int(meal_id) if meal_id else None

    if meal_id:
        editing = True
    else:
        editing = False

    reset_pending(request)

    # POST
    if request.method == "POST":
        if editing:
            new_meal = Meal.objects.get(id=meal_id,user=user)  
        else:
            new_meal = Meal(user=user) 
        return post_edit_meal(request, meal_id, editing, new_meal)
        

    if editing:
        meal = Meal.objects.get(id=meal_id, user=user)

        ingredients = meal.ingredients.all()
        ingredients = ingredients.exclude(id__in=request.session["pending_removals"])
        pending_ingredients = Ingredient.objects.filter(id__in=request.session["pending_additions"], user=user)
        combined_ingredients = list(ingredients) + list(pending_ingredients)

        return render(request, "cart/create-meal.html", {
            "meals": Meal.objects.filter(user=user),
            "editing": editing,
            "chosen_meal": meal,
            "ingredients": Ingredient.objects.filter(user=user),
            "combined_ingredients": combined_ingredients,
            "ingredients_list":  list(Ingredient.objects.filter(user=user).values_list('name', flat=True))
        })
        
    else:
        pending_ingredients = Ingredient.objects.filter(id__in=request.session["pending_additions"], user=user)

        
        category = request.GET.get('category')
        if category == 'all' or category == None:
            filtered_list = Meal.objects.filter(user=user).order_by(Lower('name'))
        else:
            filtered_list = Meal.objects.filter(category = category, user=user).order_by(Lower('name'))

        return render(request, "cart/edit-meal.html" , {
            "ingredients": Ingredient.objects.filter(user=user),
            "combined_ingredients": pending_ingredients,
            "meals": filtered_list,
            "ingredients_list":  list(Ingredient.objects.filter(user=user).values_list('name', flat=True)),
            "category": category
        })
    

def create_meal(request, meal_id = None):
    user = get_user(request)
    meal_id = request.POST.get("meal_id") or meal_id
    meal_id = int(meal_id) if meal_id else None

    if meal_id:
        editing = True
        new_meal = None
    else:
        new_meal = Meal(user=user)
        editing = False

    reset_pending(request)

    # POST
    if request.method == "POST":
        return post_edit_meal(request, meal_id, editing, new_meal)
        

    
    pending_ingredients = Ingredient.objects.filter(id__in=request.session["pending_additions"])
    

    return render(request, "cart/create-meal.html" , {
        "ingredients": Ingredient.objects.filter(user=user),
        "combined_ingredients": pending_ingredients,
        "editing": editing,
        "ingredients_list":  list(Ingredient.objects.filter(user=user).values_list('name', flat=True))
    })

def select_meal(request, slot_id = None):
    user = get_user(request)
    
    slot_id = request.POST.get('slot_id') or request.GET.get('slot_id')

    current_ids = get_current_ids(request)
    
    # if we used the button to add a meal or to reset
    if request.method == "POST":
        if request.POST.get("reset") == "true":
            return reset_meals(request)
        
        elif request.POST.get("form_type") == "remove_meal":
            remove_meal(request, current_ids, request.POST.get("removed_id") )
            return redirect(reverse('select-meal'))
        
        elif request.POST.get("form_type") == "add_meal":     
            print("THIS IS THE ID")
            print(request.POST.get("add_meal_id"))      
            add_meal(request, current_ids, request.POST.get("add_meal_id"), slot_id)
            return redirect(reverse('select-meal'))
        

    category = request.GET.get('category')
    if category == 'all' or category == None:
        filtered_list = Meal.objects.filter(user=user).order_by(Lower('name'))
    else:
        filtered_list = Meal.objects.filter(category = category, user=user).order_by(Lower('name'))
    # finally, we render the page and pass to the html the data
    # we calculated to be displayed
    return render(request, "cart/select-meal.html", {
        **get_weekly_data(current_ids, category, user),
        "meals": filtered_list,
        "slot_id": slot_id,
        "category":category
    })


def edit_ingredient(request, ing_id = None):
    user = get_user(request)

    ing_id = request.POST.get("ing_id") or ing_id
    ing_id = int(ing_id) if ing_id else None

    if ing_id:
        editing = True
    else:
        editing = False

    # POST
    if request.method == "POST":
        if editing:
            new_ing = Ingredient.objects.get(id=ing_id, user=user)
        else:
            new_ing = Ingredient(user=user)
        return post_edit_ingredient(request, ing_id, editing, new_ing)
        

    if editing:
        ing = Ingredient.objects.get(id=ing_id, user=user)

        return render(request, "cart/create-ingredient.html", {
            "editing": editing,
            "chosen_ingredient": ing,
        })
    else:
        ingredients = list(Ingredient.objects.filter(user=user).order_by(Lower('name')))
        pairs = []
        for i in range(0, len(ingredients), 2):
            pair = ingredients[i:i+2]
            if len(pair) < 2:
                pair.append(None)
            pairs.append(pair)
        
        portions = request.POST.get('portion_count')

        return render(request, "cart/ingredients.html" , {
            "ingredient_pairs": pairs,
            "portions": portions,
            "chosen_ingredient": None
        })
    

def create_ingredient(request, ing_id = None):
    user = get_user(request)

    ing_id = request.POST.get("ing_id") or ing_id
    ing_id = int(ing_id) if ing_id else None

    if ing_id:
        editing = True
        new_ing = Ingredient.objects.get(id=ing_id,user=user)
    else:
        new_ing = Ingredient(user=user)
        editing = False

    # POST
    if request.method == "POST":
        return post_edit_ingredient(request, ing_id, editing, new_ing)
        

    return render(request, "cart/create-ingredient.html" , {
        "editing": editing,
        "chosen_ingredient": new_ing if editing else None
    })


from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password):
                login(request, user)
                return redirect("user_page")
            else:
                message = "Invalid credentials"
        except User.DoesNotExist:
            message = "Invalid credentials"
        
        return render(request, "cart/login.html", {"message": message})


    if request.user.is_authenticated: # already logged in
        return redirect("user_page")
    return render(request, "cart/login.html")


def logout_view(request):
    logout(request)
    return render(request, "cart/login.html", {
        "message": "Logged out"
    })

def user_page(request):
    if not request.user.is_authenticated: # go to login page
        return redirect("login")
    return render(request, "cart/user.html") # if logged in


def create_user(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            return render(request, "cart/create_user.html", {
                "message": "Invalid inputs. Try again."
            })

        # Create username same as email (since default User requires username)
        if User.objects.filter(username=email).exists():
            return render(request, "cart/create_user.html", {
                "message": "a User with this email already exists."
            })

        user = User.objects.create_user(username=email, email=email, password=password)

        # we create some default ingredients for the user
        create_default_ingredients("carrots", 4, user)
        create_default_ingredients("tomatoes", 4, user)
        create_default_ingredients("toast bread", 8, user)


        login(request, user)
        return redirect("user_page")

    return render(request, "cart/create_user.html")


def create_default_ingredients(ing_name, ing_portions, user):
    ingredient = Ingredient(user=user)
    ingredient.portions = int(ing_portions) if ing_portions else 1
    ingredient.name = ing_name
    ingredient.user = user
    ingredient.save()