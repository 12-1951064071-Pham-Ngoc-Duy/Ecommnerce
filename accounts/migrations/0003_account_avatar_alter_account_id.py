# Generated by Django 4.2.2 on 2024-02-27 03:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20240208_1020'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='avatar',
            field=models.ImageField(null=True, upload_to='avatars/'),
        ),
        migrations.AlterField(
            model_name='account',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
