from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Ingredient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    portions = models.IntegerField(default=1)
    cost_min = models.FloatField(blank=True, null=True)
    cost_max = models.FloatField(blank=True, null=True)
    def __str__(self):
        return self.name

CATEGORY_CHOICES = [
    ('pasta', 'Pasta / Rice'),
    ('meat', 'Meat / Poultry'),
    ('fish', 'Fish / Seafood'),
    ('eggs', 'Eggs / Dairy'),
    ('other', 'Other')
]

class Meal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    category = models.CharField(max_length=16, blank=True, null=True,     choices=CATEGORY_CHOICES,)
    ingredients = models.ManyToManyField(Ingredient, related_name="meals")
    portions = models.IntegerField()
    difficulty = models.IntegerField(blank=True, null=True)
    time = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return self.name