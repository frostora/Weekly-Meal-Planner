# Generated by Django 5.2.4 on 2025-07-10 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cart", "0006_ingredient_portions"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ingredient",
            name="cost_single",
            field=models.FloatField(blank=True),
        ),
    ]
