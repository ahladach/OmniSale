# Generated by Django 3.0.7 on 2024-03-03 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_auto_20240301_0949'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stock',
            name='product_code',
        ),
        migrations.AddField(
            model_name='stock',
            name='code',
            field=models.CharField(default='', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='stock',
            name='category',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='stock',
            name='is_deleted',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AlterField(
            model_name='stock',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.DeleteModel(
            name='Category',
        ),
    ]
