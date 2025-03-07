# Generated by Django 5.1.6 on 2025-03-05 23:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_project_contract_document_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='client_type',
            field=models.CharField(blank=True, choices=[('builder', 'Builder'), ('contractor', 'Contractor'), ('municipality', 'Municipality'), ('engineer', 'Engineer'), ('general_public', 'General Public'), ('ncdot', 'NCDOT'), ('developer', 'Developer'), ('architect', 'Architect'), ('utility_company', 'Utility Company')], max_length=50, verbose_name='Client Type'),
        ),
        migrations.CreateModel(
            name='ClientEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('label', models.CharField(blank=True, help_text='E.g., Work, Personal, Assistant', max_length=100)),
                ('is_primary', models.BooleanField(default=False)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emails', to='core.client')),
            ],
            options={
                'ordering': ['-is_primary', 'email'],
            },
        ),
        migrations.CreateModel(
            name='ClientPhone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=20)),
                ('label', models.CharField(blank=True, help_text='E.g., Mobile, Office, Home', max_length=100)),
                ('is_primary', models.BooleanField(default=False)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phones', to='core.client')),
            ],
            options={
                'ordering': ['-is_primary', 'phone'],
            },
        ),
    ]
