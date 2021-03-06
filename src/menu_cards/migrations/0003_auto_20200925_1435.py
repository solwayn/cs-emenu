# Generated by Django 3.1.1 on 2020-09-25 14:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("menu_cards", "0002_auto_20200924_0717"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="menucard",
            name="dish",
        ),
        migrations.AddField(
            model_name="dish",
            name="menu_card",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="dishes",
                to="menu_cards.menucard",
            ),
        ),
        migrations.AlterField(
            model_name="dish",
            name="food_type",
            field=models.SmallIntegerField(
                blank=True,
                choices=[
                    (10, "Meat"),
                    (11, "Vegetarian"),
                    (12, "Vegan"),
                    (100, "Unknown"),
                ],
                default=10,
                help_text="Type of food",
            ),
        ),
        migrations.AlterField(
            model_name="dish",
            name="name",
            field=models.CharField(max_length=100),
        ),
        migrations.AddConstraint(
            model_name="dish",
            constraint=models.UniqueConstraint(
                fields=("name", "menu_card"), name="unique_dish_name"
            ),
        ),
    ]
