# Generated by Django 3.0.7 on 2024-04-15 23:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0013_auto_20240415_1854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salepayment',
            name='payment_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
