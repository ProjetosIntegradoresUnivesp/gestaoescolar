from django import forms
from .models import Turma, Aluno, Disciplina
from django_select2.forms import Select2MultipleWidget

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