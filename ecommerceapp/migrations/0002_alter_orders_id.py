# Generated by Django 4.2.3 on 2023-07-07 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ecommerceapp", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orders",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]