from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.views.generic.edit import FormView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from .models import Aluno, AnexoAluno, Professor, AnexoProfessor, Equipe, AnexoEquipe, Disciplina, Atendimento, AnexoDisciplina, Turma
from .forms import AnexoForm, TurmaForm

# View da home -----------------------------------------------------------------

class HomeView(TemplateView):
    template_name = 'home.html'

# View generica de uploads de anexos -------------------------------------------

TIPOS_DOCUMENTO_CHOICES = [
    ('Documento de identificação', 'Documento de identificação'),
    ('Comprovante de residência', 'Comprovante de residência'),
    ('Laudo Médico', 'Laudo Médico'),
    ('Outro', 'Outro')
]

TIPO_DOCUMENTO_DISCIPLINA_CHOICES = [
    ('Plano de Ensino', 'Plano de Ensino'),
    ('Plano de Aula', 'Plano de Aula'),
    ('Diário de Classe', 'Diário de Classe'),
    ('Lista de Lista de Frequência', 'Lista de Frequência'),
    ('Notas','Notas'),
    ('Outro','Outro')
]

class UploadAnexosView(FormView):
    template_name = 'object_upload_anexos_form.html'
    form_class = AnexoForm
    model = None  # Será definido nas subclasses
    related_name = 'anexos'

    def get_object(self):
        return self.model.objects.get(pk=self.kwargs['pk'])

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        obj = self.get_object()

        # Ajuste as escolhas do campo `tipo_documento` com base no modelo
        if isinstance(obj, Aluno):
            form.fields['tipo_documento'].choices = TIPOS_DOCUMENTO_CHOICES
        elif isinstance(obj, Disciplina):
            form.fields['tipo_documento'].choices = TIPO_DOCUMENTO_DISCIPLINA_CHOICES
        elif isinstance(obj, Professor):
            form.fields['tipo_documento'].choices = TIPOS_DOCUMENTO_CHOICES
        elif isinstance(obj, Equipe):
            form.fields['tipo_documento'].choices = TIPOS_DOCUMENTO_CHOICES

        return form

    def form_valid(self, form):
        arquivos = self.request.FILES.getlist('arquivos')
        obj = self.get_object()
        tipo_documento = form.cleaned_data['tipo_documento']

        for arquivo in arquivos:
            if isinstance(obj, Aluno):
                AnexoAluno.objects.create(aluno=obj, arquivo=arquivo, tipo_documento=tipo_documento)
            elif isinstance(obj, Professor):
                AnexoProfessor.objects.create(professor=obj, arquivo=arquivo, tipo_documento=tipo_documento)
            elif isinstance(obj, Equipe):
                AnexoEquipe.objects.create(equipe=obj, arquivo=arquivo, tipo_documento=tipo_documento)
            elif isinstance(obj, Disciplina):
                AnexoDisciplina.objects.create(disciplina=obj, arquivo=arquivo, tipo_documento=tipo_documento)

        return redirect(self.get_success_url())

    def get_success_url(self):
        # Gera a URL de redirecionamento com base no nome do modelo que originou o anexo
        if isinstance(self.get_object(), Aluno):
            return reverse('aluno_info', kwargs={'pk': self.kwargs['pk']})
        elif isinstance(self.get_object(), Disciplina):
            return reverse('disciplina_info', kwargs={'pk': self.kwargs['pk']})
        elif isinstance(self.get_object(), Professor):
            return reverse('professor_info', kwargs={'pk': self.kwargs['pk']})
        elif isinstance(self.get_object(), Equipe):
            return reverse('equipe_info', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()

        # Adiciona o objeto correto ao contexto para o template renderizar o nome
        if isinstance(obj, Aluno):
            context['aluno'] = obj
        elif isinstance(obj, Disciplina):
            context['disciplina'] = obj
        elif isinstance(obj, Professor):
            context['professor'] = obj
        elif isinstance(obj, Equipe):
            context['equipe'] = obj

        # Adiciona os anexos ao contexto
        context['anexos'] = getattr(obj, self.related_name).all()

        return context

class ExcluirAnexoView(View):
    def post(self, request, pk):
        # Tenta encontrar o anexo para alunos ou professores
        anexo_aluno = AnexoAluno.objects.filter(pk=pk).first()
        anexo_professor = AnexoProfessor.objects.filter(pk=pk).first()
        anexo_equipe = AnexoEquipe.objects.filter(pk=pk).first()
        anexo_disciplina = AnexoDisciplina.objects.filter(pk=pk).first()

        anexo = anexo_aluno or anexo_professor or anexo_equipe or anexo_disciplina

        if anexo:
            anexo.delete()
            messages.success(request, "Anexo excluído com sucesso!")
        else:
            messages.error(request, "Anexo não encontrado!")

        # Redireciona de volta para a página do objeto (aluno/professor)
        return redirect(request.META.get('HTTP_REFERER', '/'))

# Views das classes de alunos --------------------------------------------------

# View da lista de alunos

class AlunosListView(ListView):
    model = Aluno
    template_name = 'alunos_list.html'
    context_object_name = 'alunos'

    def get_queryset(self):
        # Ordena os alunos pelo nome em ordem alfabética
        return Aluno.objects.all().order_by('nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        alunos = context['alunos']

        # Cria uma lista para adicionar dados de idade e turma ativa
        for aluno in alunos:
            aluno.idade = aluno.idade  # Calcula a idade usando a propriedade
            aluno.turma_ativa = aluno.turma_ativa()  # Obtém a turma ativa usando o método

        context['alunos'] = alunos  # Atualiza a lista de alunos com os dados adicionais
        return context

# View das informações de um aluno

class AlunoInfoView(View):
    def get(self, request, *args, **kwargs):
        aluno = get_object_or_404(Aluno, pk=kwargs['pk'])

        # Passa os anexos do aluno para o contexto
        anexos = aluno.anexos.all()

        # Cria o contexto com aluno e anexos
        context = {
            'aluno': aluno,
            'anexos': anexos
        }

        return render(request, "aluno_info.html", context)

# View para cadastrar um aluno

class AlunoCreateView(CreateView):
    model = Aluno
    fields = ["id_num", "nome", "data_nascimento", "sexo", "rg", "cpf", "nome_mae",
              "cpf_mae", "nome_pai","cpf_pai","cep_residencia","bairro","endereco",
              "numero_residencia","complemento","telefone","email","historico_saude"]
    success_url = reverse_lazy("aluno_upload_anexos")
    template_name = "aluno_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Aluno cadastrado com sucesso!")
        aluno = form.save()  # Salva o aluno e retorna o objeto criado
        return redirect('aluno_upload_anexos', pk=aluno.pk)

# View para atualizar um aluno

class AlunoUpdateView(UpdateView):
    model = Aluno
    fields = ["id_num", "nome", "data_nascimento", "sexo", "rg", "cpf", "nome_mae",
              "cpf_mae", "nome_pai","cpf_pai","cep_residencia","bairro","endereco",
              "numero_residencia","complemento","telefone","email","historico_saude"]
    success_url = reverse_lazy("alunos_list")
    template_name = "aluno_form.html"

# View para upload dos anexos

class AlunoAnexosView(UploadAnexosView):
    model = Aluno
    related_name = 'anexos'


# Views das classes de professores ---------------------------------------------

# View da lista de professores

class ProfessoresListView(ListView):
    model = Professor
    template_name = 'professores_list.html'
    context_object_name = 'professores'

    def get_queryset(self):
        # Ordena os professores pelo nome em ordem alfabética
        return Professor.objects.all().order_by('nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        professores = context['professores']

        # Cria uma lista para adicionar dados de status e turma ativa
        for professor in professores:
            professor.status = professor.status  # Calcula o satus usando a propriedade
            professor.turma_ativa = professor.turma_ativa()  # Obtém a turma ativa usando o método

        context['professores'] = professores  # Atualiza a lista de professores com os dados adicionais
        return context

# View para cadastrar professor

class ProfessorCreateView(CreateView):
    model = Professor
    fields = ["id_num","nome","sexo","data_inicio","telefone","email"]
    success_url = reverse_lazy("professores_list")
    template_name = "professor_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Professor cadastrado com sucesso!")
        professor = form.save()  # Salva o professor e retorna o objeto criado
        return redirect('professor_upload_anexos', pk=professor.pk)

# View para visualizar informações de um professor

class ProfessorInfoView(View):
    def get(self, request, *args, **kwargs):
        professor = get_object_or_404(Professor, pk=kwargs['pk'])

        # Passa os anexos do professor para o contexto
        anexos = professor.anexos.all()

        # Cria o contexto com professor e anexos
        context = {
            'professor': professor,
            'anexos': anexos
        }

        return render(request, "professor_info.html", context)

# View para atualizarinformações de um professor

class ProfessorUpdateView(UpdateView):
    model = Professor
    fields = ["id_num", "nome", "sexo", "data_inicio","data_saida", "telefone", "email"]
    success_url = reverse_lazy("professores_list")
    template_name = "professor_form.html"

# View para upload de anexos de professores

class ProfessorAnexosView(UploadAnexosView):
    model = Professor
    related_name = 'anexos'


# Views das classes de equipe --------------------------------------------------

# View da lista de equipe

class EquipeListView(ListView):
    model = Equipe
    template_name = 'equipe_list.html'
    context_object_name = 'equipe'

    def get_queryset(self):
        # Ordena os membros da equipe pelo nome em ordem alfabética
        return Equipe.objects.all().order_by('nome_profissional')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        equipe = context['equipe']

        # Cria uma lista para adicionar dados de status
        for membro in equipe:
            membro.status = membro.status  # Calcula o status usando a propriedade

        context['equipe'] = equipe  # Atualiza a lista de membros da equipe com os dados adicionais
        return context

# View para cadastrar membro da equipe

class EquipeCreateView(CreateView):
    model = Equipe
    fields = ["id_num","nome_profissional","funcao","sexo","data_inicio","email","telefone"]
    success_url = reverse_lazy("equipe_list")
    template_name = "equipe_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Membro da equipe cadastrado com sucesso!")
        equipe = form.save()  # Salva o membro da equipe e retorna o objeto criado
        return redirect('equipe_upload_anexos', pk=equipe.pk)

# View para uload de anexos de equipe

class EquipeAnexosView(UploadAnexosView):
    model = Equipe
    related_name = 'anexos'

# View para visualizar informações de um membro da equipe

class EquipeInfoView(View):
    def get(self, request, *args, **kwargs):
        equipe = get_object_or_404(Equipe, pk=kwargs['pk'])

        # Passa os anexos do membro da equipe para o contexto
        anexos = equipe.anexos.all()

        # Cria o contexto com o nome 'equipe'
        context = {
            'equipe': equipe,
            'anexos': anexos
        }

        return render(request, "equipe_info.html", context)

# View para atualizar informações de um membro da equipe

class EquipeUpdateView(UpdateView):
    model = Equipe
    fields = ["id_num", "nome_profissional", "funcao", "sexo", "data_inicio", "data_saida", "email", "telefone"]
    success_url = reverse_lazy("equipe_list")
    template_name = "equipe_form.html"

# Views da classe de Atendimento -----------------------------------------------

# View para criar um atendimento
class AtendimentoCreateView(LoginRequiredMixin, CreateView):
    model = Atendimento
    fields = ['data_atendimento', 'tipo_atendimento', 'descricao', 'tipo_documento', 'anexos']
    template_name = 'atendimento_form.html'

    # Função para capturar o cargo do profissional
    def get_responsavel(self, user):
        try:
            # Verifica se o usuário é da equipe
            equipe = get_object_or_404(Equipe, user=user)
            return equipe, "Equipe", equipe.funcao  # Retorna o membro da equipe, identificação e função
        except:
            # Se não for da equipe, tenta como professor
            professor = get_object_or_404(Professor, user=user)
            return professor, "Professor", None  # Retorna o professor e a identificação

    def form_valid(self, form):
        aluno_pk = self.kwargs['pk']
        aluno = get_object_or_404(Aluno, pk=aluno_pk)

        # Utiliza a função get_responsavel para capturar o responsável e o cargo
        responsavel, cargo, funcao = self.get_responsavel(self.request.user)

        form.instance.aluno = aluno
        form.instance.responsavel_atendimento = responsavel

        # Se necessário, adicione informações de cargo ou função ao modelo
        # Exemplo:
        # form.instance.cargo_responsavel = cargo
        # form.instance.funcao_responsavel = funcao

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['aluno'] = get_object_or_404(Aluno, pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        return reverse('aluno_info', kwargs={'pk': self.kwargs['pk']})

# Views da classe de disciplinas -----------------------------------------------

# View da lista de disciplinas

class DisciplinasListView(ListView):
    model = Disciplina
    template_name = 'disciplinas_list.html'
    context_object_name = 'disciplinas'

    def get_queryset(self):
        # Ordena as disciplinas pelo nome em ordem alfabética
        return Disciplina.objects.all().order_by('codigo_disciplina')

# View para criar uma disciplina

class DisciplinaCreateView(CreateView):
    model = Disciplina
    fields = ['codigo_disciplina', 'nome_disciplina', 'professor', 'serie', 'ano_disciplina']
    template_name = 'disciplina_form.html'
    success_url = reverse_lazy('disciplina_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filtrar apenas professores ativos (sem data de saída)
        form.fields['professor'].queryset = Professor.objects.filter(data_saida__isnull=True)
        return form

    def form_valid(self, form):
        messages.success(self.request, "Disciplina cadastrada com sucesso!")
        disciplina = form.save()
        return redirect('disciplina_upload_anexos', pk=disciplina.pk)


# View para visualizar informações de uma disciplina

class DisciplinaInfoView(View):
    def get(self, request, *args, **kwargs):
        disciplina = get_object_or_404(Disciplina, pk=kwargs['pk'])

        # Recupera os anexos associados à disciplina
        anexos = disciplina.anexos.all()

        # Cria o contexto com o nome 'disciplina' e 'anexos'
        context = {
            'disciplina': disciplina,
            'anexos': anexos
        }

        return render(request, "disciplina_info.html", context)

# View para atualizar informações de uma disciplina

class DisciplinaUpdateView(UpdateView):
    model = Disciplina
    fields = ['codigo_disciplina', 'nome_disciplina', 'professor', 'serie', 'ano_disciplina']
    template_name = 'disciplina_form.html'
    success_url = reverse_lazy('disciplinas_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filtrar apenas professores ativos (sem data de saída)
        form.fields['professor'].queryset = Professor.objects.filter(data_saida__isnull=True)
        return form

# View para upload de anexos de disciplinas

class DisciplinasAnexosView(UploadAnexosView):
    model = Disciplina
    related_name = 'anexos'

# Views da classe turma --------------------------------------------------------

# View da lista de turmas

class TurmasListView(ListView):
    model = Turma
    template_name = 'turmas_list.html'
    context_object_name = 'turmas'

    def get_queryset(self):

        return Turma.objects.all().order_by('nome_turma', 'ano_turma')

# View para criar uma turma

class TurmaCreateView(CreateView):
    model = Turma
    form_class = TurmaForm
    template_name = 'turma_form.html'
    success_url = reverse_lazy('turmas_list')

    def form_valid(self, form):
        # Salva a turma e atribui automaticamente os professores com base nas disciplinas
        response = super().form_valid(form)
        self.object.atribuir_professores() # Chama o método para associar professores
        messages.success(self.request, "Turma criada com sucesso!")
        return response

# View para atualizar uma turma

class TurmaUpdateView(UpdateView):
    model = Turma
    form_class = TurmaForm
    template_name = 'turma_form.html'
    success_url = reverse_lazy('turmas_list')

    def form_valid(self, form):
        # Salva a turma e atribui automaticamente os professores com base nas disciplinas
        response = super().form_valid(form)
        self.object.atribuir_professores()  # Chama o método para associar professores
        messages.success(self.request, "Turma atualizada com sucesso!")
        return response

# View de informações da turma

class TurmaInfoView(View):
    def get(self, request, *args, **kwargs):
        turma = get_object_or_404(Turma, pk=kwargs['pk'])
        context = {
            'turma': turma,
            'alunos': turma.alunos.all(),
            'disciplinas': turma.disciplinas.all()
        }
        return render(request, "turma_info.html", context)


