# Generated by Django 5.0.6 on 2024-10-20 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car', '0006_alter_article_img_url_alter_article_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='img',
            field=models.ImageField(default='images/services/service1.png', upload_to='images/services'),
        ),
    ]
