# Generated by Django 4.2 on 2025-03-31 09:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_evenement'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evenement',
            name='individu',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='evenements', to='app.individu'),
        ),
    ]
