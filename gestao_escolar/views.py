from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, View, DetailView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.views.generic.edit import FormView, CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from rolepermissions.decorators import has_role_decorator, has_permission_decorator
from rolepermissions.permissions import revoke_permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from .models import Aluno, AnexoAluno, Professor, AnexoProfessor, Equipe, AnexoEquipe, Disciplina, Atendimento, AnexoAtendimento, AnexoDisciplina, Turma
from .forms import AnexoForm, TurmaForm, RegistroUsuarioForm, PerfilUsuario
from .models import Avaliacao, NotaAvaliacao, Disciplina
from .forms import AvaliacaoForm, NotaAvaliacaoFormSet
from .models import calcular_media_bimestre, calcular_media_final
from collections import defaultdict
from django.db.models.functions import ExtractMonth

# View da home -----------------------------------------------------------------

class HomeView(LoginRequiredMixin, TemplateView):
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

# Ajuste na UploadAnexosView para suportar Atendimento com atendimento_pk

class UploadAnexosView(FormView):
    template_name = 'object_upload_anexos_form.html'
    form_class = AnexoForm
    model = None  # Será definido nas subclasses
    related_name = 'anexos'  # Será definido nas subclasses ou conforme o modelo

    def get_object(self):
        # Identifica o objeto correto, especialmente para Atendimento que usa atendimento_pk
        if self.model == Atendimento:
            return get_object_or_404(Atendimento, pk=self.kwargs['atendimento_pk'])
        return get_object_or_404(self.model, pk=self.kwargs['pk'])

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Define as opções de tipos de documentos com base no tipo do objeto
        if isinstance(self.get_object(), (Aluno, Professor, Equipe, Atendimento)):
            form.fields['tipo_documento'].choices = TIPOS_DOCUMENTO_CHOICES
        elif isinstance(self.get_object(), Disciplina):
            form.fields['tipo_documento'].choices = TIPO_DOCUMENTO_DISCIPLINA_CHOICES
        return form

    def form_valid(self, form):
        obj = self.get_object()
        tipo_documento = form.cleaned_data['tipo_documento']
        arquivos = self.request.FILES.getlist('arquivos')

        # Salva cada arquivo com o tipo de documento específico
        for arquivo in arquivos:
            if isinstance(obj, Aluno):
                AnexoAluno.objects.create(aluno=obj, arquivo=arquivo, tipo_documento=tipo_documento)
            elif isinstance(obj, Professor):
                AnexoProfessor.objects.create(professor=obj, arquivo=arquivo, tipo_documento=tipo_documento)
            elif isinstance(obj, Equipe):
                AnexoEquipe.objects.create(equipe=obj, arquivo=arquivo, tipo_documento=tipo_documento)
            elif isinstance(obj, Disciplina):
                AnexoDisciplina.objects.create(disciplina=obj, arquivo=arquivo, tipo_documento=tipo_documento)
            elif isinstance(obj, Atendimento):
                AnexoAtendimento.objects.create(atendimento=obj, arquivo=arquivo, tipo_documento=tipo_documento)

        # Redireciona para a página de sucesso
        return redirect(self.get_success_url())

    def get_success_url(self):
        # Redireciona para a página correta conforme o tipo de objeto
        obj = self.get_object()
        if isinstance(obj, Aluno):
            return reverse('aluno_info', kwargs={'pk': self.kwargs['pk']})
        elif isinstance(obj, Disciplina):
            return reverse('disciplina_info', kwargs={'pk': self.kwargs['pk']})
        elif isinstance(obj, Professor):
            return reverse('professor_info', kwargs={'pk': self.kwargs['pk']})
        elif isinstance(obj, Equipe):
            return reverse('equipe_info', kwargs={'pk': self.kwargs['pk']})
        elif isinstance(obj, Atendimento):
            return reverse('atendimento_info', kwargs={'pk': self.kwargs['pk'], 'atendimento_pk': self.kwargs['atendimento_pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()

        # Adiciona o objeto correto ao contexto para renderização no template
        if isinstance(obj, Aluno):
            context['aluno'] = obj
        elif isinstance(obj, Disciplina):
            context['disciplina'] = obj
        elif isinstance(obj, Professor):
            context['professor'] = obj
        elif isinstance(obj, Equipe):
            context['equipe'] = obj
        elif isinstance(obj, Atendimento):
            context['atendimento'] = obj

        # Adiciona os anexos ao contexto para exibição no template
        context['anexos'] = getattr(obj, self.related_name).all()
        return context

# View para excluir anexos -----------------------------------------------------

class ExcluirAnexoView(LoginRequiredMixin, View):
    def post(self, request, pk):

        anexo = (
                AnexoAluno.objects.filter(pk=pk).first() or
                AnexoProfessor.objects.filter(pk=pk).first() or
                AnexoEquipe.objects.filter(pk=pk).first() or
                AnexoDisciplina.objects.filter(pk=pk).first()or
                AnexoAtendimento.objects.filter(pk=pk).first()
            )

        # Verifica e exclui o anexo encontrado
        if anexo:
            anexo.delete()
            messages.success(request, "Anexo excluído com sucesso!")
        else:
            messages.error(request, "Anexo não encontrado!")

        # Redireciona para a página de origem após exclusão
        return redirect(request.META.get('HTTP_REFERER', '/'))

# Views das classes de alunos --------------------------------------------------

# View da lista de alunos

class AlunosListView(LoginRequiredMixin, ListView):
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

class AlunoInfoView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        aluno = get_object_or_404(Aluno, pk=kwargs['pk'])

        # Passa os anexos do aluno para o contexto
        anexos = aluno.anexos.all()

        # Cria o contexto com aluno, anexos e funções de cálculo
        context = {
            'aluno': aluno,
            'anexos': anexos,
            'calcular_media_bimestre': calcular_media_bimestre,
            'calcular_media_final': calcular_media_final,
        }

        return render(request, "aluno_info.html", context)

# View para cadastrar um aluno

class AlunoCreateView(LoginRequiredMixin, CreateView):
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

class AlunoUpdateView(LoginRequiredMixin, UpdateView):
    model = Aluno
    fields = ["id_num", "nome", "data_nascimento", "sexo", "rg", "cpf", "nome_mae",
              "cpf_mae", "nome_pai","cpf_pai","cep_residencia","bairro","endereco",
              "numero_residencia","complemento","telefone","email","historico_saude"]
    success_url = reverse_lazy("alunos_list")
    template_name = "aluno_form.html"

# View para upload dos anexos

class AlunoAnexosView(LoginRequiredMixin, UploadAnexosView):
    model = Aluno
    related_name = 'anexos'


# Views das classes de professores ---------------------------------------------

# View da lista de professores

class ProfessoresListView(LoginRequiredMixin, ListView):
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

class ProfessorCreateView(LoginRequiredMixin, CreateView):
    model = Professor
    fields = ["id_num","nome","sexo","data_inicio","telefone","email"]
    success_url = reverse_lazy("professores_list")
    template_name = "professor_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Professor cadastrado com sucesso!")
        professor = form.save()  # Salva o professor e retorna o objeto criado
        return redirect('professor_upload_anexos', pk=professor.pk)

# View para visualizar informações de um professor

class ProfessorInfoView(LoginRequiredMixin, View):
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

class ProfessorUpdateView(LoginRequiredMixin, UpdateView):
    model = Professor
    fields = ["id_num", "nome", "sexo", "data_inicio","data_saida", "telefone", "email"]
    success_url = reverse_lazy("professores_list")
    template_name = "professor_form.html"

# View para upload de anexos de professores

class ProfessorAnexosView(LoginRequiredMixin, UploadAnexosView):
    model = Professor
    related_name = 'anexos'


# Views das classes de equipe --------------------------------------------------

# View da lista de equipe

class EquipeListView(LoginRequiredMixin, ListView):
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

class EquipeCreateView(LoginRequiredMixin, CreateView):
    model = Equipe
    fields = ["id_num","nome_profissional","funcao","sexo","data_inicio","email","telefone"]
    success_url = reverse_lazy("equipe_list")
    template_name = "equipe_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Membro da equipe cadastrado com sucesso!")
        equipe = form.save()  # Salva o membro da equipe e retorna o objeto criado
        return redirect('equipe_upload_anexos', pk=equipe.pk)

# View para uload de anexos de equipe

class EquipeAnexosView(LoginRequiredMixin, UploadAnexosView):
    model = Equipe
    related_name = 'anexos'

# View para visualizar informações de um membro da equipe

class EquipeInfoView(LoginRequiredMixin, View):
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

class EquipeUpdateView(LoginRequiredMixin, UpdateView):
    model = Equipe
    fields = ["id_num", "nome_profissional", "funcao", "sexo", "data_inicio", "data_saida", "email", "telefone"]
    success_url = reverse_lazy("equipe_list")
    template_name = "equipe_form.html"

# Views da classe de Atendimento -----------------------------------------------

# View para criar um atendimento

class AtendimentoCreateView(LoginRequiredMixin, CreateView):
    model = Atendimento
    fields = ['data_atendimento', 'tipo_atendimento', 'descricao']
    template_name = 'atendimento_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Busca o aluno antes de processar a view
        self.aluno = get_object_or_404(Aluno, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.aluno = self.aluno
        user = self.request.user

        # Verifica se o usuário tem um `PerfilUsuario` associado para definir a função
        try:
            perfil_usuario = user.perfilusuario  # Certifique-se de que o nome aqui corresponde ao seu modelo
            if perfil_usuario.professor:
                form.instance.responsavel_content_type = ContentType.objects.get_for_model(Professor)
                form.instance.responsavel_object_id = perfil_usuario.professor.pk
                form.instance.funcao = "Professor"  # Define a função como "Professor" para o perfil de professor
            elif perfil_usuario.equipe:
                form.instance.responsavel_content_type = ContentType.objects.get_for_model(Equipe)
                form.instance.responsavel_object_id = perfil_usuario.equipe.pk
                form.instance.funcao = perfil_usuario.equipe.funcao  # Usa a função da equipe
            else:
                messages.error(self.request, "Erro: Perfil do usuário não está vinculado a um professor ou membro da equipe.")
                return self.form_invalid(form)
        except PerfilUsuario.DoesNotExist:
            messages.error(self.request, "Erro: Nenhum perfil de responsável encontrado.")
            return self.form_invalid(form)

        # Salva o atendimento no banco de dados e confirma
        try:
            atendimento = form.save()
            messages.success(self.request, "Atendimento criado com sucesso!")
            return redirect(reverse('atendimento_info', kwargs={'pk': self.aluno.pk, 'atendimento_pk': atendimento.pk}))
        except Exception as e:
            messages.error(self.request, f"Erro ao salvar atendimento: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "O formulário não é válido. Por favor, revise os campos.")
        return render(self.request, self.template_name, {"form": form, "aluno": self.aluno})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['aluno'] = self.aluno
        return context


# View para visualizar informações de um atendimento


class AtendimentoInfoView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Busca o atendimento específico usando atendimento_pk e o aluno com pk
        atendimento = get_object_or_404(Atendimento, pk=kwargs['atendimento_pk'], aluno__pk=kwargs['pk'])

        # Recupera os anexos associados ao atendimento usando o related_name correto
        anexos = atendimento.anexos_atendimento.all()

        # Cria o contexto com o nome 'atendimento' e os anexos
        context = {
            'atendimento': atendimento,
            'anexos': anexos
        }

        return render(request, "atendimento_info.html", context)

# View para atualizar um atendimento

class AtendimentoUpdateView(LoginRequiredMixin, UpdateView):
    model = Atendimento
    fields = ['data_atendimento', 'tipo_atendimento', 'descricao']
    template_name = 'atendimento_form.html'

    def get_object(self):
        atendimento_pk = self.kwargs['atendimento_pk']
        return get_object_or_404(Atendimento, pk=atendimento_pk)

    def form_valid(self, form):
        response = super().form_valid(form)
        arquivos = self.request.FILES.getlist('arquivos')
        for arquivo in arquivos:
            AnexoAtendimento.objects.create(
                atendimento=self.object,
                arquivo=arquivo,
                tipo_documento=form.cleaned_data['tipo_documento']
            )
        messages.success(self.request, "Atendimento atualizado com sucesso!")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        atendimento = self.get_object()
        context['aluno'] = atendimento.aluno
        context['anexos'] = atendimento.anexos_atendimento.all()
        return context

    def get_success_url(self):
        return reverse('atendimento_info', kwargs={'pk': self.kwargs['pk'], 'atendimento_pk': self.object.pk})


# View de anexo da disciplina:

class AtendimentoAnexosView(LoginRequiredMixin, UploadAnexosView):
    model = Atendimento
    related_name = 'anexos_atendimento'

# Views da classe de disciplinas -----------------------------------------------

# View da lista de disciplinas

class DisciplinasListView(LoginRequiredMixin, ListView):
    model = Disciplina
    template_name = 'disciplinas_list.html'
    context_object_name = 'disciplinas'

    def get_queryset(self):
        # Ordena as disciplinas pelo nome em ordem alfabética
        return Disciplina.objects.all().order_by('codigo_disciplina')

# View para criar uma disciplina

class DisciplinaCreateView(LoginRequiredMixin, CreateView):
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
        disciplina = form.save()
        # Associa a disciplina ao professor selecionado
        if disciplina.professor:
            disciplina.professor.disciplinas.add(disciplina)
        messages.success(self.request, "Disciplina cadastrada com sucesso!")
        return redirect('disciplina_upload_anexos', pk=disciplina.pk)

# View para visualizar informações de uma disciplina

class DisciplinaInfoView(LoginRequiredMixin, View):
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

class DisciplinaUpdateView(LoginRequiredMixin, UpdateView):
    model = Disciplina
    fields = ['codigo_disciplina', 'nome_disciplina', 'professor', 'serie', 'ano_disciplina']
    template_name = 'disciplina_form.html'
    success_url = reverse_lazy('disciplinas_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filtrar apenas professores ativos (sem data de saída)
        form.fields['professor'].queryset = Professor.objects.filter(data_saida__isnull=True)
        return form

    def form_valid(self, form):
        disciplina = form.save(commit=False)

        # Remove a disciplina do professor antigo, se houver mudança
        disciplina_atual = Disciplina.objects.get(pk=disciplina.pk)
        if disciplina_atual.professor and disciplina_atual.professor != disciplina.professor:
            disciplina_atual.professor.disciplinas.remove(disciplina_atual)

        # Adiciona a disciplina ao novo professor
        if disciplina.professor:
            disciplina.professor.disciplinas.add(disciplina)

        disciplina.save()
        messages.success(self.request, "Disciplina atualizada com sucesso!")
        return redirect('disciplinas_list')

# View para upload de anexos de disciplinas

class DisciplinasAnexosView(LoginRequiredMixin, UploadAnexosView):
    model = Disciplina
    related_name = 'anexos'

# Views da classe turma --------------------------------------------------------

# View da lista de turmas

class TurmasListView(LoginRequiredMixin, ListView):
    model = Turma
    template_name = 'turmas_list.html'
    context_object_name = 'turmas'

    def get_queryset(self):

        return Turma.objects.all().order_by('nome_turma', 'ano_turma')

# View para criar uma turma

class TurmaCreateView(LoginRequiredMixin, CreateView):
    model = Turma
    form_class = TurmaForm
    template_name = 'turma_form.html'
    success_url = reverse_lazy('turmas_list')

def form_valid(self, form):
        turma = form.save()

        # Atribui professores às turmas com base nas disciplinas selecionadas
        turma.atribuir_professores()

        # Adiciona a turma aos alunos selecionados
        for aluno in form.cleaned_data['alunos']:
            aluno.turmas_aluno.add(turma)

        # Adiciona a turma aos professores associados às disciplinas selecionadas
        for professor in turma.professores.all():
            professor.turmas_professor.add(turma)

        messages.success(self.request, "Turma criada com sucesso!")
        return redirect(self.success_url)

# View para atualizar uma turma

class TurmaUpdateView(LoginRequiredMixin, UpdateView):
    model = Turma
    form_class = TurmaForm
    template_name = 'turma_form.html'
    success_url = reverse_lazy('turmas_list')

    def form_valid(self, form):
        turma = form.save(commit=False)

        # Atualiza os alunos da turma
        turma.alunos.set(form.cleaned_data['alunos'])

        # Atualiza as disciplinas da turma
        turma.disciplinas.set(form.cleaned_data['disciplinas'])

        # Atribui professores baseados nas disciplinas selecionadas
        professores = set()
        for disciplina in turma.disciplinas.all():
            if disciplina.professor:
                disciplina.professor.turmas_professor.add(turma)
                professores.add(disciplina.professor)

        turma.professores.set(professores)  # Atualiza os professores da turma com os professores das disciplinas

        turma.save()
        messages.success(self.request, "Turma atualizada com sucesso!")
        return redirect(self.success_url)

# View de informações da turma

class TurmaInfoView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        turma = get_object_or_404(Turma, pk=kwargs['pk'])
        context = {
            'turma': turma,
            'alunos': turma.alunos.all(),
            'disciplinas': turma.disciplinas.all()
        }
        return render(request, "turma_info.html", context)

# View para registrar um usuário

def assign_role(user, perfil):
    """Define a função do usuário com base no perfil associado."""
    if perfil.professor:
        user.role = "Professor"
    elif perfil.equipe:
        funcao = perfil.equipe.funcao
        if funcao == "Diretoria":
            user.role = "diretoria"
        elif funcao == "Coordenação":
            user.role = "coordenacao"
        elif funcao == "Secretaria":
            user.role = "secretaria"
        elif funcao in ["Psicólogo", "Assistente Social", "Pedagogo"]:
            user.role = "apoio"
        else:
            user.role = "outros"
    user.save()

def registrar_usuario(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redireciona para a home se o usuário já está autenticado

    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            # Cria o usuário e define a senha
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            # Cria o perfil do usuário
            perfil = PerfilUsuario(usuario=user)

            # Define automaticamente o perfil como Professor ou Equipe
            if form.is_professor:
                perfil.professor = get_object_or_404(Professor, email=user.email)
            else:
                perfil.equipe = get_object_or_404(Equipe, email=user.email)
            perfil.save()

            # Atribui a função ao usuário
            assign_role(user, perfil)

            # Exibe mensagem de sucesso e redireciona para a página de login
            messages.success(request, "Usuário registrado com sucesso! Faça login para acessar.")
            return redirect("login")
        else:
            # Mostra mensagens de erro no formulário
            print(form.errors)
    else:
        form = RegistroUsuarioForm()

    return render(request, "registro.html", {"form": form})

# View para login

class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True
    success_url = '/'  # Redireciona para a home após login

    def get_success_url(self):
        return self.success_url

# Views para notas e avaliações -----------------------------------------------

class AvaliacaoCreateView(CreateView):
    model = Avaliacao
    form_class = AvaliacaoForm
    template_name = 'avaliacao_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.disciplina = get_object_or_404(Disciplina, pk=self.kwargs['disciplina_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['disciplina'] = self.disciplina
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['disciplina'] = self.disciplina
        return context

    def get_success_url(self):
        return reverse('disciplina_info', kwargs={'pk': self.disciplina.pk})

    def form_valid(self, form):
        messages.success(self.request, "Avaliação criada e notas dos alunos geradas!")
        return super().form_valid(form)

class NotaAvaliacaoUpdateView(View):
    template_name = 'nota_avaliacao_form.html'

    def get(self, request, *args, **kwargs):
        self.avaliacao = get_object_or_404(Avaliacao, pk=self.kwargs['avaliacao_pk'])
        formset = NotaAvaliacaoFormSet(queryset=self.avaliacao.notas_avaliacao.all())
        return render(request, self.template_name, {
            'formset': formset,
            'avaliacao': self.avaliacao
        })

    def post(self, request, *args, **kwargs):
        self.avaliacao = get_object_or_404(Avaliacao, pk=self.kwargs['avaliacao_pk'])
        formset = NotaAvaliacaoFormSet(request.POST, queryset=self.avaliacao.notas_avaliacao.all())

        if formset.is_valid():
            formset.save()  # SIMPLES, DIRETO
            messages.success(request, "Notas salvas com sucesso!")
            return redirect('disciplina_info', pk=self.avaliacao.disciplina.pk)

        return render(request, self.template_name, {
            'formset': formset,
            'avaliacao': self.avaliacao
        })


# View para o dashboard -------------------------------------------------------

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Visão geral
        context['num_funcionarios'] = Equipe.objects.count()
        context['num_professores'] = Professor.objects.count()
        context['num_alunos'] = Aluno.objects.count()
        context['num_turmas'] = Turma.objects.count()

        # Média de turmas por professor (correta agora)
        professores = Professor.objects.annotate(num_turmas=Count('turmas_professor'))
        total_professores = professores.count()
        total_turmas = sum(professor.num_turmas for professor in professores)
        media_turmas_por_professor = (total_turmas / total_professores) if total_professores else 0
        context['media_turmas_por_professor'] = round(media_turmas_por_professor, 1)

        # Médias dos bimestres
        medias_bimestres = {}
        for bimestre in range(1, 5):
            media_bimestre = NotaAvaliacao.objects.filter(avaliacao__bimestre=bimestre).aggregate(avg_nota=Avg('nota'))['avg_nota']
            medias_bimestres[bimestre] = round(media_bimestre, 2) if media_bimestre else None
        context['medias_bimestres'] = medias_bimestres

        media_final_geral = NotaAvaliacao.objects.aggregate(avg_nota=Avg('nota'))['avg_nota']
        context['media_final_geral'] = round(media_final_geral, 2) if media_final_geral else None

        # Professores por disciplina
        professores_por_disciplina = (
            Disciplina.objects
            .values('nome_disciplina')
            .annotate(num_professores=Count('professor', distinct=True))
            .order_by('nome_disciplina')
        )
        context['professores_por_disciplina'] = professores_por_disciplina

        # Médias de alunos
        medias_alunos_disciplinas = (
            NotaAvaliacao.objects
            .values('aluno__id_num', 'aluno__nome', 'avaliacao__disciplina__codigo_disciplina', 'avaliacao__disciplina__nome_disciplina')
            .annotate(media_aluno=Avg('nota'))
            .order_by('aluno__nome')[:50]
        )
        context['medias_alunos_disciplinas'] = medias_alunos_disciplinas

        # Filtros
        context['turmas'] = Turma.objects.all().order_by('nome_turma')
        context['disciplinas'] = Disciplina.objects.all().order_by('nome_disciplina')
        context['alunos'] = Aluno.objects.all().order_by('nome')

        return context

class DashboardDataAPIView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        turma_id = request.GET.get('turma_id')
        disciplina_id = request.GET.get('disciplina_id')
        aluno_id = request.GET.get('aluno_id')

        notas = NotaAvaliacao.objects.all()
        atendimentos = Atendimento.objects.all()

        if turma_id:
            notas = notas.filter(aluno__turmas_aluno__id=turma_id)
            atendimentos = atendimentos.filter(aluno__turmas_aluno__id=turma_id)
        if disciplina_id:
            notas = notas.filter(avaliacao__disciplina__id=disciplina_id)
        if aluno_id:
            notas = notas.filter(aluno__id=aluno_id)
            atendimentos = atendimentos.filter(aluno__id=aluno_id)

        tabela = (
            notas
            .values(
                'aluno__id_num',
                'aluno__nome',
                'avaliacao__disciplina__codigo_disciplina',
                'avaliacao__disciplina__nome_disciplina'
            )
            .annotate(media_aluno=Avg('nota'))
        )

        medias_bimestres = {}
        for b in range(1, 5):
            media = notas.filter(avaliacao__bimestre=b).aggregate(m=Avg('nota'))['m']
            medias_bimestres[b] = round(media, 2) if media else 0

        media_final = notas.aggregate(m=Avg('nota'))['m']
        media_final = round(media_final, 2) if media_final else 0

        disciplinas = (
            notas.values('avaliacao__disciplina__nome_disciplina')
            .annotate(
                m1=Avg('nota', filter=Q(avaliacao__bimestre=1)),
                m2=Avg('nota', filter=Q(avaliacao__bimestre=2)),
                m3=Avg('nota', filter=Q(avaliacao__bimestre=3)),
                m4=Avg('nota', filter=Q(avaliacao__bimestre=4)),
                mf=Avg('nota')
            )
        )
        disciplinas_data = [
            {
                'nome_disciplina': d['avaliacao__disciplina__nome_disciplina'],
                'medias_bimestres': [
                    round(d['m1'] or 0, 2),
                    round(d['m2'] or 0, 2),
                    round(d['m3'] or 0, 2),
                    round(d['m4'] or 0, 2),
                    round(d['mf'] or 0, 2)
                ]
            }
            for d in disciplinas
        ]

        atendimentos_totais = (
            atendimentos
            .values('aluno__nome')
            .annotate(total=Count('id'))
            .order_by('-total')[:10]
        )
        atendimentos_totais_data = [
            {'nome': item['aluno__nome'], 'total': item['total']}
            for item in atendimentos_totais
        ]

        atendimentos_bimestre = defaultdict(int)
        for at in atendimentos:
            mes = at.data_atendimento.month
            if mes in [1, 2, 3]:
                atendimentos_bimestre[1] += 1
            elif mes in [4, 5, 6]:
                atendimentos_bimestre[2] += 1
            elif mes in [7, 8, 9]:
                atendimentos_bimestre[3] += 1
            elif mes in [10, 11, 12]:
                atendimentos_bimestre[4] += 1

        return JsonResponse({
            'tabela': list(tabela),
            'medias_bimestres': medias_bimestres,
            'media_final': media_final,
            'disciplinas': disciplinas_data,
            'atendimentos_totais': atendimentos_totais_data,
            'atendimentos_bimestre': dict(atendimentos_bimestre),
        })
