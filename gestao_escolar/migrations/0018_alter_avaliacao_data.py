# Generated by Django 5.2 on 2025-04-26 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gestao_escolar", "0017_remove_avaliacao_turma"),
    ]

    operations = [
        migrations.AlterField(
            model_name="avaliacao",
            name="data",
            field=models.DateField(blank=True, null=True),
        ),
    ]
