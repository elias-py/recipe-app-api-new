# Generated by Django 3.2.15 on 2022-09-21 02:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='tag',
            field=models.ManyToManyField(to='core.Tag'),
        ),
    ]
