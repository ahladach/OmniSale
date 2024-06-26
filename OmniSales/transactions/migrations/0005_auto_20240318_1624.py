# Generated by Django 3.0.7 on 2024-03-18 21:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_auto_20240316_0741'),
        ('transactions', '0004_auto_20240318_1451'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='saleitem',
            name='stock',
        ),
        migrations.AddField(
            model_name='saleitem',
            name='product',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='saleitem', to='inventory.Stock'),
        ),
        migrations.AlterField(
            model_name='purchaseitem',
            name='category',
            field=models.ForeignKey(limit_choices_to={'is_deleted': False}, on_delete=django.db.models.deletion.CASCADE, related_name='purchase_items', to='inventory.Stock'),
        ),
    ]
