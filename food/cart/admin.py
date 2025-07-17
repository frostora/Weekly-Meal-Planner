from django.contrib import admin
from .models import Meal, Ingredient

class IngredientsAdmin(admin.ModelAdmin):
    list_display = ("name", "portions")

class MealsAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "portions")

admin.site.register(Meal, MealsAdmin)
admin.site.register(Ingredient, IngredientsAdmin)