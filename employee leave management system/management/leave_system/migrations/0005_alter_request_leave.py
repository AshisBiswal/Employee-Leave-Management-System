# Generated by Django 5.0.4 on 2024-05-07 16:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leave_system', '0004_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='leave',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request', to='leave_system.leave'),
        ),
    ]