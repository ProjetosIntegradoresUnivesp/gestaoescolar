# Generated by Django 5.1.1 on 2024-09-15 01:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gestao_escolar", "0003_alter_equipe_funcao"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="disciplina",
            name="anexos",
        ),
        migrations.AddField(
            model_name="disciplina",
            name="ano_disciplina",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="aluno",
            name="sexo",
            field=models.CharField(
                blank=True,
                choices=[("Masculino", "Masculino"), ("Feminino", "Feminino")],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="equipe",
            name="sexo",
            field=models.CharField(
                blank=True,
                choices=[("Masculino", "Masculino"), ("Feminino", "Feminino")],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="professor",
            name="sexo",
            field=models.CharField(
                blank=True,
                choices=[("Masculino", "Masculino"), ("Feminino", "Feminino")],
                max_length=10,
                null=True,
            ),
        ),
    ]
