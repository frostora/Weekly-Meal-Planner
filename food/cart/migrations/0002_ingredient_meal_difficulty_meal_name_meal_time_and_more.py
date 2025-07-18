# Generated by Django 5.2.4 on 2025-07-10 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cart", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Ingredient",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=64)),
                ("cost_min", models.IntegerField()),
                ("cost_max", models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name="meal",
            name="difficulty",
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="meal",
            name="name",
            field=models.CharField(default=1, max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="meal",
            name="time",
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="meal",
            name="ingredients",
            field=models.ManyToManyField(
                related_name="ingredients", to="cart.ingredient"
            ),
        ),
    ]
