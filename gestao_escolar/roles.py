from rolepermissions.roles import AbstractUserRole

class Diretor(AbstractUserRole):
    available_permissions = {
        'criar_turma': True,
        'editar_turma': True,
        'excluir_turma': True,
        'criar_aluno': True,
        'editar_aluno': True,
        'excluir_aluno': True,
        'criar_professor': True,
        'editar_professor': True,
        'excluir_professor': True,
        'criar_disciplina': True,
        'editar_disciplina': True,
        'excluir_disciplina': True,
        'criar_avaliacao': True,
        'editar_avaliacao': True,
        'excluir_avaliacao': True,
    }

class Professor:
    available_permissions = {
      'criar_avaliacao': True,
      'editar_avaliacao': True,
      'excluir_avaliacao': True,
        }
