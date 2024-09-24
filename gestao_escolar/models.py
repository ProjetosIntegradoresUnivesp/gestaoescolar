from django.db import models
from datetime import date

# Definir as opções possiveis

TIPOS_DOCUMENTO_CHOICES = [
    ('Documento de identificação', 'Documento de identificação'),
    ('Comprovante de residência', 'Comprovante de residência'),
    ('Laudo Médico', 'Laudo Médico'),
    ('Outro', 'Outro')
]

SEXO_CHOICES = [
    ('Masculino', 'Masculino'),
    ('Feminino', 'Feminino')
]

# Modelo para Equipe
class Equipe(models.Model):
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

    def status(self):
        return 'Ativo' if self.data_saida is None else 'Inativo'

    def turma_ativa(self):
        ano_atual = date.today().year
        turmas_ativas = self.turmas.filter(ano_turma=ano_atual)
        return turmas_ativas.first() if turmas_ativas.exists() else None

# Modelo para Anexos de Professores (semelhante ao AnexoAluno)
class AnexoProfessor(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name='anexos')
    arquivo = models.FileField(upload_to='documentos/professores/')
    tipo_documento = models.CharField(max_length=50, choices=TIPOS_DOCUMENTO_CHOICES)

    def __str__(self):
        return f"{self.tipo_documento} - {self.arquivo.name}"

class Turma(models.Model):
    nome_turma = models.CharField(max_length=255)  # Especificado max_length
    ano_turma = models.IntegerField()
    professores = models.ManyToManyField(Professor, related_name='turmas_professor')
    disciplinas = models.ManyToManyField('Disciplina', related_name='turmas_disciplina')
    alunos = models.ManyToManyField('Aluno', related_name='turmas_aluno')

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

# Modelo para Disciplinas
class Disciplina(models.Model):
    TIPO_DOCUMENTO_DISCIPLINA_CHOICES = [
    ('Plano de Ensino', 'Plano de Ensino'),
    ('Plano de Aula', 'Plano de Aula'),
    ('Lista de frequencia', 'Lista de Frequência'),
    ('Outro', 'Outro')
    ]
    codigo_disciplina = models.CharField(max_length=50, unique=True)
    nome_disciplina = models.CharField(max_length=255)
    professor = models.ForeignKey(Professor, on_delete=models.SET_NULL, null=True, related_name='disciplinas_professor')
    ano_disciplina = models.IntegerField(null=True, blank=True)
    notas = models.ManyToManyField('Aluno', through='Nota', related_name='notas_aluno')
    frequencias = models.ManyToManyField('Aluno', through='Frequencia', related_name='frequencias_aluno')
    tipo_documento = models.CharField(max_length=50, choices=TIPO_DOCUMENTO_DISCIPLINA_CHOICES, null=True, blank=True)

    def disciplina_ativa(self):
        ano_atual = date.today().year
        disciplinas = self.disciplinas.filter(ano_disciplina=ano_atual)
        if disciplinas.exists():
            return disciplinas.first()
        return None


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

# Modelo para Atendimentos
class Atendimento(models.Model):
    data_atendimento = models.DateField()
    tipo_atendimento = models.CharField(max_length=255)
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='atendimentos_aluno')  # Removido null=True
    responsavel_atendimento = models.ForeignKey(Equipe, on_delete=models.SET_NULL, null=True, related_name='responsavel_atendimento')
    descricao = models.TextField()
    tipo_documento = models.CharField(max_length=50, choices=TIPOS_DOCUMENTO_CHOICES, null=True, blank=True)
    anexos = models.FileField(upload_to='documentos/atendimentos/', null=True, blank=True)
