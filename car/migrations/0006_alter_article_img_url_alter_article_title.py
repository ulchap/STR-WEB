# Generated by Django 5.0.6 on 2024-10-01 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car', '0005_remove_cart_is_active_remove_cart_updated_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='img_url',
            field=models.ImageField(upload_to='images/articles'),
        ),
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.CharField(max_length=100),
        ),
    ]
