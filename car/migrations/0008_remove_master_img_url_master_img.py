# Generated by Django 5.0.6 on 2024-10-28 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car', '0007_service_img'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='master',
            name='img_url',
        ),
        migrations.AddField(
            model_name='master',
            name='img',
            field=models.ImageField(default='images/services/service1.png', upload_to='images/masters'),
        ),
    ]
