import re
from django import forms
from django.contrib.auth.models import User
from django_select2.forms import Select2MultipleWidget
from django.core.exceptions import ValidationError
from .models import Turma, Aluno, Disciplina, PerfilUsuario, Professor, Equipe

class AnexoForm(forms.Form):
    tipo_documento = forms.ChoiceField(choices=[])

class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = ['codigo_turma','nome_turma', 'serie', 'ano_turma', 'alunos', 'disciplinas']
        widgets = {
            'alunos': Select2MultipleWidget(attrs={'class': 'form-control'}),
            'disciplinas': Select2MultipleWidget(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(TurmaForm, self).__init__(*args, **kwargs)
        # Ordenar a lista de alunos e disciplinas em ordem alfabética
        self.fields['alunos'].queryset = Aluno.objects.all().order_by('nome')
        self.fields['disciplinas'].queryset = Disciplina.objects.all().order_by('nome_disciplina')

# Formulário para registro de usuários -----------------------------------------

class RegistroUsuarioForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not re.match(r'^[a-z0-9]+\.[a-z0-9]+$', username):
            raise forms.ValidationError("O nome de usuário deve estar no formato nome.sobrenome, em minúsculas, e pode conter números.")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nome de usuário já está em uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")

        # Verifica se o email pertence a um Professor ou a um membro da Equipe
        professor_exists = Professor.objects.filter(email=email).exists()
        equipe_exists = Equipe.objects.filter(email=email).exists()

        # Retorna erro se o email não estiver cadastrado em nenhuma das classes
        if not professor_exists and not equipe_exists:
            raise ValidationError("O email informado não está cadastrado como professor ou membro da equipe.")

        # Armazena o tipo de perfil encontrado para uso posterior no método save
        self.is_professor = professor_exists
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            perfil = PerfilUsuario(usuario=user)

            # Define o perfil como Professor ou Equipe com base no resultado da validação do email
            if self.is_professor:
                perfil.professor = Professor.objects.get(email=user.email)
            else:
                perfil.equipe = Equipe.objects.get(email=user.email)
            perfil.save()
        return user
