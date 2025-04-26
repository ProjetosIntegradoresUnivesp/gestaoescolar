from django import template
from gestao_escolar.models import calcular_media_bimestre, calcular_media_final

register = template.Library()

@register.simple_tag
def media_bimestre(disciplina, aluno, bimestre):
    return calcular_media_bimestre(disciplina, aluno, bimestre)

@register.simple_tag
def media_final(disciplina, aluno):
    return calcular_media_final(disciplina, aluno)
