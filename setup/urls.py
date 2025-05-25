from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from gestao_escolar.views import HomeView,ExcluirAnexoView
from gestao_escolar.views import AlunosListView, AlunoInfoView, AlunoCreateView, AlunoUpdateView, AlunoAnexosView
from gestao_escolar.views import ProfessoresListView, ProfessorCreateView, ProfessorInfoView, ProfessorUpdateView, ProfessorAnexosView
from gestao_escolar.views import EquipeListView, EquipeCreateView, EquipeInfoView, EquipeUpdateView, EquipeAnexosView
from gestao_escolar.views import DisciplinasListView, DisciplinaCreateView, DisciplinaInfoView, DisciplinaUpdateView,DisciplinasAnexosView
from gestao_escolar.views import TurmasListView, TurmaCreateView, TurmaInfoView, TurmaUpdateView
from gestao_escolar.views import AtendimentoCreateView, AtendimentoInfoView, AtendimentoUpdateView, AtendimentoAnexosView
from gestao_escolar.views import CustomLoginView, registrar_usuario
from gestao_escolar.views import AvaliacaoCreateView, NotaAvaliacaoUpdateView
from gestao_escolar.views import DashboardView, DashboardDataAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page = 'login'), name='logout'),  # Define para onde redirecionar após logout
    path('', HomeView.as_view(), name="home"),  # Usando .as_view() para a CBV
    path('alunos/', AlunosListView.as_view(), name="alunos_list"),  # Usando .as_view() para a CBV
    path("alunos/info/<int:pk>/", AlunoInfoView.as_view(), name="aluno_info"),
    path("alunos/create/", AlunoCreateView.as_view(), name="aluno_create"),
    path("alunos/update/<int:pk>/", AlunoUpdateView.as_view(), name="aluno_update"),
    path("alunos/upload_anexos/<int:pk>/", AlunoAnexosView.as_view(), name="aluno_upload_anexos"),
    path("professores/", ProfessoresListView.as_view(), name="professores_list"),
    path("professores/create/", ProfessorCreateView.as_view(), name="professor_create"),
    path("professores/info/<int:pk>/", ProfessorInfoView.as_view(), name="professor_info"),
    path("professores/update/<int:pk>/", ProfessorUpdateView.as_view(), name="professor_update"),
    path("professores/upload_anexos/<int:pk>/", ProfessorAnexosView.as_view(), name="professor_upload_anexos"),
    path('anexos/excluir/<int:pk>/', ExcluirAnexoView.as_view(), name='excluir_anexo'),
    path('equipe/', EquipeListView.as_view(), name="equipe_list"),
    path('equipe/create/', EquipeCreateView.as_view(), name="equipe_create"),
    path('equipe/info/<int:pk>/', EquipeInfoView.as_view(), name="equipe_info"),
    path('equipe/update/<int:pk>/', EquipeUpdateView.as_view(), name="equipe_update"),
    path('equipe/upload_anexos/<int:pk>/', EquipeAnexosView.as_view(), name="equipe_upload_anexos"),
    path('aluno/<int:pk>/atendimento/novo/', AtendimentoCreateView.as_view(), name='atendimento_create'),
    path('aluno/<int:pk>/atendimento/info/<int:atendimento_pk>/', AtendimentoInfoView.as_view(), name='atendimento_info'),
    path('aluno/<int:pk>/atendimento/update/<int:atendimento_pk>/', AtendimentoUpdateView.as_view(), name='atendimento_update'),
    path('aluno/<int:pk>/atendimento/<int:atendimento_pk>/upload_anexos/', AtendimentoAnexosView.as_view(), name='atendimento_upload_anexos'),
    path('disciplinas/', DisciplinasListView.as_view(), name='disciplinas_list'),
    path('disciplinas/create/', DisciplinaCreateView.as_view(), name='disciplina_create'),
    path('disciplinas/info/<int:pk>/', DisciplinaInfoView.as_view(), name='disciplina_info'),
    path('disciplinas/update/<int:pk>/', DisciplinaUpdateView.as_view(), name='disciplina_update'),
    path('disciplinas/upload_anexos/<int:pk>/', DisciplinasAnexosView.as_view(), name='disciplina_upload_anexos'),
    path('turmas/', TurmasListView.as_view(), name='turmas_list'),
    path('turmas/create/', TurmaCreateView.as_view(), name='turma_create'),
    path('turmas/info/<int:pk>/', TurmaInfoView.as_view(), name='turma_info'),
    path('turmas/update/<int:pk>/', TurmaUpdateView.as_view(), name='turma_update'),
    path("registrar/", registrar_usuario, name="registrar_usuario"),
    path('disciplinas/<int:disciplina_pk>/avaliacoes/create/', AvaliacaoCreateView.as_view(), name='avaliacao_create'),
    path('avaliacoes/<int:avaliacao_pk>/notas/', NotaAvaliacaoUpdateView.as_view(), name='nota_avaliacao_update'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard-data/', DashboardDataAPIView.as_view(), name='dashboard_data'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # para servir arquivos de mídia durante o desenvolvimento