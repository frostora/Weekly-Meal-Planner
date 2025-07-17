from django.urls import path
from . import views
  
urlpatterns = [
    path("", views.index, name = "index"),
    path("about", views.about, name = "about"),
    path("contact", views.contact, name = "contact"),
    path("select-meal", views.select_meal, name = "select-meal"),
    path("create-meal", views.create_meal, name="create-meal"),
    path("edit-meal", views.edit_meal, name="edit-meals-view"),
    path("edit-meal/<int:meal_id>", views.edit_meal, name="edit-specific-meal"),
    path("ingredients", views.edit_ingredient, name="edit-ingredients-view"),
    path("ingredients/<int:ing_id>", views.edit_ingredient, name="edit-specific-ingredient"),
    path("create-ingredient", views.create_ingredient, name="create-ingredient"),
    path("login", views.login_view, name = "login"),
    path("logout", views.logout_view, name = "logout"),
    path("user", views.user_page, name = "user_page"),
    path("create-user", views.create_user, name = "create_user"),
]