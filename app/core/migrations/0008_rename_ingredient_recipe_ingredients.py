# Generated by Django 3.2.16 on 2022-12-03 19:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_recipe_ingredient'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='ingredient',
            new_name='ingredients',
        ),
    ]
