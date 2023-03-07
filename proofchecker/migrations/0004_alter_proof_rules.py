# Generated by Django 3.2.7 on 2023-02-25 01:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proofchecker', '0003_proof_complete'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proof',
            name='rules',
            field=models.CharField(choices=[('tfl_basic', 'TFL - Basic Rules Only'), ('test_option', 'TEST-OPTION'), ('tfl_derived', 'TFL - Basic & Derived Rules'), ('fol_basic', 'FOL - Basic Rules Only'), ('fol_derived', 'FOL - Basic & Derived Rules')], default='tfl_basic', max_length=255),
        ),
    ]
