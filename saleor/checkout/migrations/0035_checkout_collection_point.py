# Generated by Django 3.2.2 on 2021-06-17 11:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("warehouse", "0014_auto_20210520_0846"),
        ("checkout", "0034_remove_checkout_quantity"),
    ]

    operations = [
        migrations.AddField(
            model_name="checkout",
            name="collection_point",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="checkouts",
                to="warehouse.warehouse",
            ),
        ),
    ]
