from django.db import models
from datetime import date
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


# Definir as opções possiveis para os campos de seleção

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

SERIE_CHOICES = [
    ('Educação Infantil', 'Educação Infantil'),
    ('1º Ano', '1º Ano'),
    ('2º Ano', '2º Ano'),
    ('3º Ano', '3º Ano'),
    ('4º Ano', '4º Ano'),
    ('5º Ano', '5º Ano'),
    ('6º Ano', '6º Ano'),
    ('7º Ano', '7º Ano'),
    ('8º Ano', '8º Ano'),
    ('9º Ano', '9º Ano'),
    ('Ensino Médio - 1º Ano', 'Ensino Médio - 1º Ano'),
    ('Ensino Médio - 2º Ano', 'Ensino Médio - 2º Ano'),
    ('Ensino Médio - 3º Ano', 'Ensino Médio - 3º Ano'),
]

SEXO_CHOICES = [
    ('Masculino', 'Masculino'),
    ('Feminino', 'Feminino')
]

FUNCAO_CHOICES = [('Diretoria','Diretoria'),
    ('Secretaria','Secretaria'),
    ('Coordenação','Coordenação'),
    ('Psicólogo','Psicólogo'),
    ('Assistente Social','Assistente Social'),
    ('Pedagogo','Pedagogo'),
    ('Auxiliar de Serviços Gerais','Auxiliar de Serviços Gerais'),
    ('Cozinheiro','Cozinheiro'),
    ('Merendeira','Merendeira'),
    ('Inspetor','Inspetor'),
    ('Vigia','Vigia'),
    ('Outro','Outro')
]

# Modelo para professores ----------------------------------------------

# Modelo para Professores
class Professor(models.Model):
    id_num = models.CharField(max_length=50, unique=True)
    nome = models.CharField(max_length=255)
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES,null=True, blank=True)
    data_inicio = models.DateField()
    data_saida = models.DateField(null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    turmas = models.ManyToManyField('Turma', related_name='professores_turma')
    disciplinas = models.ManyToManyField('Disciplina', blank=True, related_name='professores_disciplina')
    tipo_documento = models.CharField(max_length=50, choices=TIPOS_DOCUMENTO_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.nome

    def status(self):
        return 'Ativo' if self.data_saida is None else 'Inativo'

    def turma_ativa(self):
        ano_atual = date.today().year
        turmas_ativas = self.turmas.filter(ano_turma=ano_atual)
        return turmas_ativas.first() if turmas_ativas.exists() else None

# Modelo para Anexos de Professores
class AnexoProfessor(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name='anexos')
    arquivo = models.FileField(upload_to='documentos/professores/')
    tipo_documento = models.CharField(max_length=50, choices=TIPOS_DOCUMENTO_CHOICES)

    def __str__(self):
        return f"{self.tipo_documento} - {self.arquivo.name}"

# Modelo para Equipe ----------------------------------------------

# Modelo para Equipe
class Equipe(models.Model):
    id_num = models.CharField(max_length=50, unique=True)
    nome_profissional = models.CharField(max_length=255)
    funcao = models.CharField(max_length=255, choices=FUNCAO_CHOICES)
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES, null=True, blank=True)
    data_inicio = models.DateField()
    data_saida = models.DateField(null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    telefone = models.CharField(max_length=20,null=True, blank=True)
    tipo_documento = models.CharField(max_length=50, choices=TIPOS_DOCUMENTO_CHOICES, null=True, blank=True)

    def status(self):
        # Retorna 'ativo' se a data de saída for None, caso contrário, 'inativo'
        return 'Ativo' if self.data_saida is None else 'Inativo'

# Modelo para Anexos de Equipe

class AnexoEquipe(models.Model):
    equipe = models.ForeignKey(Equipe, on_delete=models.CASCADE, related_name='anexos')
    arquivo = models.FileField(upload_to='documentos/equipe/')
    tipo_documento = models.CharField(max_length=50, choices=TIPOS_DOCUMENTO_CHOICES)

    def __str__(self):
        return f"{self.tipo_documento} - {self.arquivo.name}"

# Modelo para Turmas ----------------------------------------------

# Modelo para Turmas ----------------------------------------------

class Turma(models.Model):
    codigo_turma = models.CharField(max_length=50, unique=True, blank=True, null=True)
    nome_turma = models.CharField(max_length=255)
    ano_turma = models.IntegerField()
    serie = models.CharField(max_length=50, choices=SERIE_CHOICES, blank=True, null=True)
    alunos = models.ManyToManyField('Aluno', related_name='turmas_aluno')
    disciplinas = models.ManyToManyField('Disciplina', related_name='turmas_disciplina')
    professores = models.ManyToManyField('Professor', related_name='turmas_professor', blank=True)  # Alterei o related_name aqui

    def status(self):
        if date.today().year == self.ano_turma:
            return 'Ativa'
        return 'Inativa'

    def atribuir_professores(self):
        professores = Professor.objects.filter(disciplinas__in=self.disciplinas.all()).distinct()
        self.professores.set(professores)

    def save(self, *args, **kwargs):
        super(Turma, self).save(*args, **kwargs)
        self.atribuir_professores()

    def __str__(self):
        return self.nome_turma

# Modelo para alunos ----------------------------------------------

# Modelo para Alunos

class Aluno(models.Model):
    id_num = models.CharField(max_length=50, unique=True)
    nome = models.CharField(max_length=255)
    data_nascimento = models.DateField()
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES, null=True, blank=True)
    rg = models.CharField(max_length=20)
    cpf = models.CharField(max_length=14)
    nome_mae = models.CharField(max_length=255)
    cpf_mae = models.CharField(max_length=14)
    nome_pai = models.CharField(max_length=255, null=True, blank=True)
    cpf_pai = models.CharField(max_length=14, null=True, blank=True)
    cep_residencia = models.CharField(max_length=9)
    bairro = models.CharField(max_length=100)
    endereco = models.CharField(max_length=255)
    numero_residencia = models.CharField(max_length=10)
    complemento = models.CharField(max_length=100, null=True, blank=True)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(max_length=255, null=True, blank=True)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='alunos_turma', null=True, blank=True)
    disciplinas = models.ManyToManyField('Disciplina', through='AlunoDisciplina', blank=True)
    historico_saude = models.TextField(null=True, blank=True)
    atendimentos = models.ManyToManyField('Atendimento', related_name='aluno_atendimentos', blank=True)
    tipo_documento = models.CharField(max_length=50, choices=TIPOS_DOCUMENTO_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.nome

    def idade(self):
        today = date.today()
        return today.year - self.data_nascimento.year - ((today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day))

    def turma_ativa(self):
        ano_atual = date.today().year
        turmas = self.turmas_aluno.filter(ano_turma=ano_atual)
        if turmas.exists():
            return turmas.first()
        return None

# Modelo para os anexos dos alunos:

class AnexoAluno(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='anexos')
    arquivo = models.FileField(upload_to='documentos/alunos/')
    tipo_documento = models.CharField(max_length=50, choices=TIPOS_DOCUMENTO_CHOICES)

    def __str__(self):
        return f"{self.tipo_documento} - {self.arquivo.name}"

# Modelo para Atendimentos ----------------------------------------------

# Modelo para Atendimentos

class Atendimento(models.Model):
    data_atendimento = models.DateField()
    tipo_atendimento = models.CharField(max_length=255)
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='atendimentos_aluno')
    responsavel_content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    responsavel_object_id = models.PositiveIntegerField()
    responsavel_atendimento = GenericForeignKey('responsavel_content_type', 'responsavel_object_id')
    descricao = models.TextField()
    tipo_documento = models.CharField(max_length=50, choices=TIPOS_DOCUMENTO_CHOICES, null=True, blank=True)
    anexos = models.FileField(upload_to='documentos/atendimentos/', null=True, blank=True)
    codigo_atendimento = models.CharField(max_length=6, unique=True, editable=False, blank=True)


    def save(self, *args, **kwargs):
        if not self.codigo_atendimento:
            # Calcula o próximo número de atendimento e padroniza para 6 dígitos
            ultimo_atendimento = Atendimento.objects.all().order_by('id').last()
            if ultimo_atendimento:
                novo_codigo = int(ultimo_atendimento.codigo_atendimento) + 1
            else:
                novo_codigo = 1
            self.codigo_atendimento = str(novo_codigo).zfill(6)
        super(Atendimento, self).save(*args, **kwargs)

    def __str__(self):
        return f"Atendimento {self.codigo_atendimento} - {self.tipo_atendimento}"

# Anexo para Atendimentos

class AnexoAtendimento(models.Model):
    atendimento = models.ForeignKey(Atendimento, on_delete=models.CASCADE, related_name='anexos_atendimento')
    arquivo = models.FileField(upload_to='documentos/atendimentos')
    tipo_documento = models.CharField(max_length=50, choices=TIPOS_DOCUMENTO_CHOICES)

    def __str__(self):
        return f"{self.tipo_documento} - {self.arquivo.name}"

# Modelos para disciplinas ----------------------------------------------

# Modelo para Disciplinas

class Disciplina(models.Model):
    codigo_disciplina = models.CharField(max_length=50, unique=True)
    nome_disciplina = models.CharField(max_length=255)
    professor = models.ForeignKey(Professor, on_delete=models.SET_NULL, null=True, related_name='professores_disciplina')
    serie = models.CharField(max_length=50, choices=SERIE_CHOICES,blank=True, null=True)
    ano_disciplina = models.IntegerField(null=True, blank=True)
    notas = models.ManyToManyField('Aluno', through='Nota', related_name='notas_aluno')
    frequencias = models.ManyToManyField('Aluno', through='Frequencia', related_name='frequencias_aluno')
    tipo_documento = models.CharField(max_length=50, choices=TIPO_DOCUMENTO_DISCIPLINA_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.codigo_disciplina

    def disciplina_ativa(self):
        ano_atual = date.today().year
        return self.ano_disciplina == ano_atual

# Modelo para Anexos de Disciplinas

class AnexoDisciplina(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='anexos')
    arquivo = models.FileField(upload_to='documentos/disciplinas/')
    tipo_documento = models.CharField(max_length=50, choices=TIPO_DOCUMENTO_DISCIPLINA_CHOICES)

    def __str__(self):
        return f"{self.tipo_documento} - {self.arquivo.name}"

# Modelo intermediário para Aluno e Disciplina (definido após Disciplina)

class AlunoDisciplina(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    data_matricula = models.DateField()

# Modelo para Notas
class Nota(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    atividade = models.CharField(max_length=255)
    nota = models.DecimalField(max_digits=5, decimal_places=2)

# Modelo para Frequências
class Frequencia(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    data = models.DateField()
    presente = models.BooleanField()

# Criar modelo para usuários ----------------------------------------------

# Modelo para Usuários

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, null=True, blank=True, related_name="perfil")
    equipe = models.ForeignKey(Equipe, on_delete=models.CASCADE, null=True, blank=True, related_name="perfil")

    def __str__(self):
        return self.usuario.username

