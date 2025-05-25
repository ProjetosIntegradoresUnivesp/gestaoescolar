from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from decimal import Decimal
from .models import (
    Aluno, Professor, Equipe, Turma, Disciplina, Atendimento, 
    AnexoAluno, AnexoProfessor, AnexoEquipe, AnexoDisciplina,
    PerfilUsuario, Avaliacao, NotaAvaliacao, calcular_media_bimestre,
    calcular_media_final
)
from .forms import RegistroUsuarioForm, TurmaForm


class AlunoModelTest(TestCase):
    """Testes para o modelo Aluno"""
    
    def setUp(self):
        self.aluno = Aluno.objects.create(
            id_num="ALU001",
            nome="João Silva",
            data_nascimento=date(2010, 5, 15),
            sexo="Masculino",
            rg="123456789",
            cpf="123.456.789-01",
            nome_mae="Maria Silva",
            cpf_mae="987.654.321-02",
            nome_pai="José Silva",
            cpf_pai="456.789.123-03",
            cep_residencia="01234-567",
            bairro="Centro",
            endereco="Rua das Flores, 123",
            numero_residencia="123",
            telefone="(11) 99999-9999",
            email="joao@email.com"
        )

    def test_str_method(self):
        """Testa se o método __str__ retorna o nome do aluno"""
        self.assertEqual(str(self.aluno), "João Silva")

    def test_idade_calculation(self):
        """Testa o cálculo da idade do aluno"""
        expected_age = date.today().year - 2010
        if (date.today().month, date.today().day) < (5, 15):
            expected_age -= 1
        self.assertEqual(self.aluno.idade(), expected_age)

    def test_unique_id_num(self):
        """Testa se o id_num é único"""
        with self.assertRaises(Exception):
            Aluno.objects.create(
                id_num="ALU001",  # Mesmo ID
                nome="Outro Aluno",
                data_nascimento=date(2010, 1, 1),
                rg="987654321",
                cpf="111.222.333-44",
                nome_mae="Outra Mãe",
                cpf_mae="555.666.777-88"
            )


class ProfessorModelTest(TestCase):
    """Testes para o modelo Professor"""
    
    def setUp(self):
        self.professor = Professor.objects.create(
            id_num="PROF001",
            nome="Ana Costa",
            sexo="Feminino",
            data_inicio=date(2020, 1, 15),
            email="ana@escola.com",
            telefone="(11) 88888-8888"
        )

    def test_str_method(self):
        """Testa se o método __str__ retorna o nome do professor"""
        self.assertEqual(str(self.professor), "Ana Costa")

    def test_status_ativo(self):
        """Testa se professor sem data de saída está ativo"""
        self.assertEqual(self.professor.status(), "Ativo")

    def test_status_inativo(self):
        """Testa se professor com data de saída está inativo"""
        self.professor.data_saida = date.today()
        self.professor.save()
        self.assertEqual(self.professor.status(), "Inativo")


class EquipeModelTest(TestCase):
    """Testes para o modelo Equipe"""
    
    def setUp(self):
        self.equipe = Equipe.objects.create(
            id_num="EQ001",
            nome_profissional="Carlos Santos",
            funcao="Coordenação",
            sexo="Masculino",
            data_inicio=date(2019, 3, 10),
            email="carlos@escola.com"
        )

    def test_status_ativo(self):
        """Testa se membro da equipe sem data de saída está ativo"""
        self.assertEqual(self.equipe.status(), "Ativo")

    def test_status_inativo(self):
        """Testa se membro da equipe com data de saída está inativo"""
        self.equipe.data_saida = date.today()
        self.equipe.save()
        self.assertEqual(self.equipe.status(), "Inativo")


class TurmaModelTest(TestCase):
    """Testes para o modelo Turma"""
    
    def setUp(self):
        self.turma = Turma.objects.create(
            codigo_turma="T001",
            nome_turma="3º Ano A",
            ano_turma=date.today().year,
            serie="3º Ano"
        )

    def test_str_method(self):
        """Testa se o método __str__ retorna o nome da turma"""
        self.assertEqual(str(self.turma), "3º Ano A")

    def test_status_ativa(self):
        """Testa se turma do ano atual está ativa"""
        self.assertEqual(self.turma.status(), "Ativa")

    def test_status_inativa(self):
        """Testa se turma de ano anterior está inativa"""
        self.turma.ano_turma = date.today().year - 1
        self.turma.save()
        self.assertEqual(self.turma.status(), "Inativa")


class DisciplinaModelTest(TestCase):
    """Testes para o modelo Disciplina"""
    
    def setUp(self):
        self.professor = Professor.objects.create(
            id_num="PROF001",
            nome="Maria Santos",
            data_inicio=date(2020, 1, 1)
        )
        self.disciplina = Disciplina.objects.create(
            codigo_disciplina="MAT001",
            nome_disciplina="Matemática",
            professor=self.professor,
            serie="3º Ano",
            ano_disciplina=date.today().year
        )

    def test_str_method(self):
        """Testa se o método __str__ retorna o código da disciplina"""
        self.assertEqual(str(self.disciplina), "MAT001")

    def test_disciplina_ativa(self):
        """Testa se disciplina do ano atual está ativa"""
        self.assertTrue(self.disciplina.disciplina_ativa())

    def test_disciplina_inativa(self):
        """Testa se disciplina de ano anterior está inativa"""
        self.disciplina.ano_disciplina = date.today().year - 1
        self.disciplina.save()
        self.assertFalse(self.disciplina.disciplina_ativa())


class AtendimentoModelTest(TestCase):
    """Testes para o modelo Atendimento"""
    
    def setUp(self):
        self.aluno = Aluno.objects.create(
            id_num="ALU001",
            nome="Pedro Silva",
            data_nascimento=date(2010, 1, 1),
            rg="123456789",
            cpf="123.456.789-01",
            nome_mae="Ana Silva",
            cpf_mae="987.654.321-02"
        )
        self.professor = Professor.objects.create(
            id_num="PROF001",
            nome="Carlos Costa",
            data_inicio=date(2020, 1, 1)
        )
        # Obter ContentType para Professor
        from django.contrib.contenttypes.models import ContentType
        self.professor_content_type = ContentType.objects.get_for_model(Professor)

    def test_codigo_atendimento_auto_generated(self):
        """Testa se o código do atendimento é gerado automaticamente"""
        atendimento = Atendimento.objects.create(
            data_atendimento=date.today(),
            tipo_atendimento="Psicológico",
            aluno=self.aluno,
            responsavel_content_type=self.professor_content_type,
            responsavel_object_id=self.professor.id,
            descricao="Atendimento de apoio"
        )
        self.assertEqual(atendimento.codigo_atendimento, "000001")

    def test_codigo_atendimento_sequential(self):
        """Testa se os códigos são sequenciais"""
        atendimento1 = Atendimento.objects.create(
            data_atendimento=date.today(),
            tipo_atendimento="Psicológico",
            aluno=self.aluno,
            responsavel_content_type=self.professor_content_type,
            responsavel_object_id=self.professor.id,
            descricao="Primeiro atendimento"
        )
        atendimento2 = Atendimento.objects.create(
            data_atendimento=date.today(),
            tipo_atendimento="Pedagógico",
            aluno=self.aluno,
            responsavel_content_type=self.professor_content_type,
            responsavel_object_id=self.professor.id,
            descricao="Segundo atendimento"
        )
        self.assertEqual(atendimento1.codigo_atendimento, "000001")
        self.assertEqual(atendimento2.codigo_atendimento, "000002")


class AvaliacaoModelTest(TestCase):
    """Testes para o modelo Avaliacao"""
    
    def setUp(self):
        self.professor = Professor.objects.create(
            id_num="PROF001",
            nome="Ana Silva",
            data_inicio=date(2020, 1, 1)
        )
        self.disciplina = Disciplina.objects.create(
            codigo_disciplina="PORT001",
            nome_disciplina="Português",
            professor=self.professor,
            serie="5º Ano",
            ano_disciplina=date.today().year
        )
        self.turma = Turma.objects.create(
            codigo_turma="T001",
            nome_turma="5º Ano A",
            ano_turma=date.today().year,
            serie="5º Ano"
        )
        self.aluno = Aluno.objects.create(
            id_num="ALU001",
            nome="João Santos",
            data_nascimento=date(2012, 3, 15),
            rg="123456789",
            cpf="123.456.789-01",
            nome_mae="Maria Santos",
            cpf_mae="987.654.321-02",
            turma=self.turma
        )
        self.turma.disciplinas.add(self.disciplina)
        self.turma.alunos.add(self.aluno)

    def test_str_method(self):
        """Testa se o método __str__ está correto"""
        avaliacao = Avaliacao.objects.create(
            disciplina=self.disciplina,
            tipo="Prova",
            bimestre=1,
            data=date.today()
        )
        expected = f"Prova - {self.disciplina.nome_disciplina} (1º Bimestre)"
        self.assertEqual(str(avaliacao), expected)

    def test_create_notas_on_save(self):
        """Testa se as notas são criadas automaticamente para todos os alunos"""
        avaliacao = Avaliacao.objects.create(
            disciplina=self.disciplina,
            tipo="Prova",
            bimestre=1,
            data=date.today()
        )
        # Verifica se foi criada uma nota para o aluno
        self.assertTrue(
            NotaAvaliacao.objects.filter(
                avaliacao=avaliacao,
                aluno=self.aluno
            ).exists()
        )


class MediaCalculationTest(TestCase):
    """Testes para cálculo de médias"""
    
    def setUp(self):
        self.professor = Professor.objects.create(
            id_num="PROF001",
            nome="Ana Silva",
            data_inicio=date(2020, 1, 1)
        )
        self.disciplina = Disciplina.objects.create(
            codigo_disciplina="MAT001",
            nome_disciplina="Matemática",
            professor=self.professor,
            serie="5º Ano",
            ano_disciplina=date.today().year
        )
        self.turma = Turma.objects.create(
            codigo_turma="T001",
            nome_turma="5º Ano A",
            ano_turma=date.today().year,
            serie="5º Ano"
        )
        self.aluno = Aluno.objects.create(
            id_num="ALU001",
            nome="Maria Santos",
            data_nascimento=date(2012, 3, 15),
            rg="123456789",
            cpf="123.456.789-01",
            nome_mae="Ana Santos",
            cpf_mae="987.654.321-02",
            turma=self.turma
        )
        self.turma.disciplinas.add(self.disciplina)
        self.turma.alunos.add(self.aluno)

    def test_calcular_media_bimestre(self):
        """Testa o cálculo da média do bimestre"""
        # Criar avaliações
        avaliacao1 = Avaliacao.objects.create(
            disciplina=self.disciplina,
            tipo="Prova",
            bimestre=1,
            data=date.today()
        )
        avaliacao2 = Avaliacao.objects.create(
            disciplina=self.disciplina,
            tipo="Seminário",
            bimestre=1,
            data=date.today()
        )
        
        # Adicionar notas
        NotaAvaliacao.objects.filter(
            avaliacao=avaliacao1,
            aluno=self.aluno
        ).update(nota=Decimal('8.0'))
        
        NotaAvaliacao.objects.filter(
            avaliacao=avaliacao2,
            aluno=self.aluno
        ).update(nota=Decimal('9.0'))
        
        # Calcular média
        media = calcular_media_bimestre(self.disciplina, self.aluno, 1)
        self.assertEqual(media, Decimal('8.5'))

    def test_calcular_media_final(self):
        """Testa o cálculo da média final"""
        # Criar avaliações para diferentes bimestres
        for bimestre in range(1, 5):
            avaliacao = Avaliacao.objects.create(
                disciplina=self.disciplina,
                tipo="Prova",
                bimestre=bimestre,
                data=date.today()
            )
            NotaAvaliacao.objects.filter(
                avaliacao=avaliacao,
                aluno=self.aluno
            ).update(nota=Decimal('8.0'))
        
        # Calcular média final
        media_final = calcular_media_final(self.disciplina, self.aluno)
        self.assertEqual(media_final, Decimal('8.0'))


class RegistroUsuarioFormTest(TestCase):
    """Testes para o formulário de registro de usuários"""
    
    def setUp(self):
        self.professor = Professor.objects.create(
            id_num="PROF001",
            nome="Ana Silva",
            data_inicio=date(2020, 1, 1),
            email="ana@escola.com"
        )

    def test_valid_form(self):
        """Testa formulário válido"""
        form_data = {
            'username': 'ana.silva',
            'email': 'ana@escola.com',
            'password': 'senha123'
        }
        form = RegistroUsuarioForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_username_format(self):
        """Testa formato inválido de username"""
        form_data = {
            'username': 'ana silva',  # Espaço não permitido
            'email': 'ana@escola.com',
            'password': 'senha123'
        }
        form = RegistroUsuarioForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_email_not_registered(self):
        """Testa email não cadastrado"""
        form_data = {
            'username': 'joao.silva',
            'email': 'joao@naoexiste.com',  # Email não cadastrado
            'password': 'senha123'
        }
        form = RegistroUsuarioForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class TurmaFormTest(TestCase):
    """Testes para o formulário de turma"""
    
    def setUp(self):
        self.aluno = Aluno.objects.create(
            id_num="ALU001",
            nome="João Silva",
            data_nascimento=date(2010, 1, 1),
            rg="123456789",
            cpf="123.456.789-01",
            nome_mae="Maria Silva",
            cpf_mae="987.654.321-02"
        )
        self.professor = Professor.objects.create(
            id_num="PROF001",
            nome="Ana Costa",
            data_inicio=date(2020, 1, 1)
        )
        self.disciplina = Disciplina.objects.create(
            codigo_disciplina="MAT001",
            nome_disciplina="Matemática",
            professor=self.professor,
            serie="3º Ano",
            ano_disciplina=date.today().year
        )

    def test_valid_form(self):
        """Testa formulário válido"""
        form_data = {
            'codigo_turma': 'T001',
            'nome_turma': '3º Ano A',
            'serie': '3º Ano',
            'ano_turma': date.today().year,
            'alunos': [self.aluno.id],
            'disciplinas': [self.disciplina.id]
        }
        form = TurmaForm(data=form_data)
        self.assertTrue(form.is_valid())


class ViewsTest(TestCase):
    """Testes básicos para as views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test.user',
            password='testpass123',
            email='test@test.com'
        )

    def test_home_view_requires_login(self):
        """Testa se a view home requer login"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)  # Redirect para login

    def test_home_view_with_login(self):
        """Testa acesso à view home com usuário logado"""
        self.client.login(username='test.user', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)


class ModelRelationshipTest(TestCase):
    """Testes para relacionamentos entre modelos"""
    
    def setUp(self):
        self.professor = Professor.objects.create(
            id_num="PROF001",
            nome="Ana Silva",
            data_inicio=date(2020, 1, 1)
        )
        self.disciplina = Disciplina.objects.create(
            codigo_disciplina="MAT001",
            nome_disciplina="Matemática",
            professor=self.professor,
            serie="5º Ano",
            ano_disciplina=date.today().year
        )
        self.turma = Turma.objects.create(
            codigo_turma="T001",
            nome_turma="5º Ano A",
            ano_turma=date.today().year,
            serie="5º Ano"
        )
        self.aluno = Aluno.objects.create(
            id_num="ALU001",
            nome="João Santos",
            data_nascimento=date(2012, 3, 15),
            rg="123456789",
            cpf="123.456.789-01",
            nome_mae="Maria Santos",
            cpf_mae="987.654.321-02",
            turma=self.turma
        )

    def test_professor_disciplina_relationship(self):
        """Testa relacionamento entre professor e disciplina"""
        self.assertEqual(self.disciplina.professor, self.professor)
        self.assertIn(self.disciplina, self.professor.professores_disciplina.all())

    def test_turma_aluno_relationship(self):
        """Testa relacionamento entre turma e aluno"""
        self.turma.alunos.add(self.aluno)
        self.assertIn(self.aluno, self.turma.alunos.all())
        self.assertIn(self.turma, self.aluno.turmas_aluno.all())

    def test_turma_disciplina_relationship(self):
        """Testa relacionamento entre turma e disciplina"""
        self.turma.disciplinas.add(self.disciplina)
        self.assertIn(self.disciplina, self.turma.disciplinas.all())
        self.assertIn(self.turma, self.disciplina.turmas_disciplina.all())
