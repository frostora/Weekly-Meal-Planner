# Generated by Django 5.2.4 on 2025-07-10 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cart", "0010_alter_meal_category_alter_meal_difficulty_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="meal",
            name="portions",
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
