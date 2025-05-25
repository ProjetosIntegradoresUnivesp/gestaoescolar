# Software de Gestão Escolar

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://dashboard.render.com/)
[![Tests](https://img.shields.io/badge/tests-41%20passing-brightgreen)](#-testes-unitários)
[![Coverage](https://img.shields.io/badge/coverage-60%25-yellow)](#resultados-de-cobertura-de-testes)
[![Django](https://img.shields.io/badge/Django-5.1-092E20?logo=django)](https://djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://python.org/)
[![Deploy](https://img.shields.io/badge/deploy-Render-46E3B7?logo=render)](https://dashboard.render.com/)

Software com framework web e script web (JavaScript), com uso de API, banco de dados em nuvem, acessibilidade, teste e controle de versão para ferramenta digital de gestão escolar desenvolvido para a disciplina de Projeto Integrador para os cursos de Bacharelado em Tecnologia da Informação Ciência de Dados e Engenharia da Computação da Universidade Virtual do Estado de São Paulo.

## 🔗 Links Importantes

- 🌐 **Deploy em Produção**: [Sistema em funcionamento no Render](https://gestaoescolarunivesp.onrender.com)
- 📊 **Dashboard CI/CD**: [Monitoramento de builds](https://dashboard.render.com/)
- 📋 **Documentação de Testes**: [TESTES_RESUMO.md](./TESTES_RESUMO.md)
- 🏗️ **Repositório**: [GitHub do Projeto](https://github.com/ProjetosIntegradoresUnivesp/gestaoescolar)

## 📈 Status do Projeto

| Aspecto | Status | Detalhes |
|---------|--------|----------|
| **🏗️ Build** | ✅ **Passando** | Deploy automático via Render |
| **🧪 Testes** | ✅ **41/41 Passing** | 100% dos testes aprovados |
| **📊 Cobertura** | ⚠️ **60%** | Modelos: 96%, Views: 38% |
| **🚀 Deploy** | ✅ **Ativo** | Produção estável no Render |
| **📱 Responsivo** | ✅ **Sim** | Interface adaptável |
| **♿ Acessibilidade** | ✅ **Implementada** | Leitor de tela, contraste |

# Equipe de Desenvolvimento

UNIVERSIDADE VIRTUAL DO ESTADO DE SÃO PAULO

* [Bruna Michelle Sargenti Moreira](https://github.com/BrunaMoreira100)
* [Diego Nespolon Bertazzoli](https://github.com/diegobertazzoli)
* [Elson Atushi Kondo](https://github.com/EAKUNIVESP)
* [Fabiana Santos Lima Sugamele](https://github.com/fabianasugamele)
* [Gabriel Silva Nascimento](https://github.com/Gabriel-GSN)
* [Glauco Bernadino Coelho]()
* [Luciana Lima Dos Santos](https://github.com/lucianalds11)
* [Nelson Francisco Correa Netto](https://github.com/nelsoncorrea)

# Problema da comunidade

A gestão escolar enfrenta dificuldades devido ao uso de arquivos em papel, em razão de limitações das ferramentas atuais, o que resulta em perda frequente de documentos, dificuldade de localização, escassez de espaço para armazenamento e desorganização. Essas limitações comprometem a eficiência e a segurança na gestão dos dados escolares.

# Objetivos do projeto

O projeto teve como objetivo desenvolver uma Ferramenta Digital Web-Based para Gestão Escolar que possibilite a criação de um banco de dados com a funcionalidade de registro do histórico dos atendimentos realizados, bem como a inserção e digitalização de informações médicas durante o período que o aluno estiver matriculado até o descarte desse registro, conforme tabela de temporalidade da guarda documental que a unidade escolar está sujeita, possibilitando a busca deste  momento de futuros atendimentos, sem a necessidade de busca em arquivos físicos.

# Funcionalidades

* Cadastro de alunos (incluindo histórico de saúde), professores, equipe de colaboradores, diciplinas e turmas.
* Sistema de registro e gestão de atendimentos escolares.
* Sistema de gestão de disciplinas e turmas.
* Gerenciamento de documentos e anexos.
* Sistema de criação e gerenciamento de usários com login e senha.
* Acessibilida de software: Avatar de leitura de tela, contraste de cores e leitor de tela.

# Pré-requisitos para execução

* Framework web - Django 5.1
* Banco de dados - PostgreSQL
* Node.js (utilizado para as APIs)
* Python 3.8+

# Como executar o projeto

## 1. Configuração do ambiente

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd gestaoescolar

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual (Windows)
venv\Scripts\activate

# Ative o ambiente virtual (Linux/Mac)
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

## 2. Configuração do banco de dados

Configure as variáveis de ambiente no arquivo `.env`:

```
SECRET_KEY=sua-chave-secreta
DEBUG=True
DATABASE_URL=postgres://usuario:senha@localhost:5432/nome_do_banco
```

## 3. Execute as migrações

```bash
python manage.py migrate
```

## 4. Crie um superusuário

```bash
python manage.py createsuperuser
```

## 5. Execute o servidor

```bash
python manage.py runserver
```

# Testes Unitários

O projeto inclui uma suíte abrangente de testes unitários que cobrem:

- **Modelos**: Testes para todos os modelos (Aluno, Professor, Equipe, Turma, Disciplina, Atendimento, etc.)
- **Formulários**: Validação de formulários de registro e criação de turmas
- **Views**: Testes básicos de acesso e autenticação
- **Relacionamentos**: Testes de integridade dos relacionamentos entre modelos
- **Cálculos**: Testes para funções de cálculo de médias e notas

## Como executar os testes

### Executar todos os testes
```bash
python manage.py test
```

### Executar testes de um app específico
```bash
python manage.py test gestao_escolar
```

### Executar uma classe de teste específica
```bash
python manage.py test gestao_escolar.tests.AlunoModelTest
```

### Executar um teste específico
```bash
python manage.py test gestao_escolar.tests.AlunoModelTest.test_idade_calculation
```

### Executar testes com verbosidade
```bash
python manage.py test --verbosity=2
```

### Verificar cobertura de testes (opcional)

Para verificar a cobertura dos testes, instale o coverage:

```bash
pip install coverage
```

Execute os testes com coverage:

```bash
# Executar testes com coverage
coverage run --source='.' manage.py test

# Gerar relatório no terminal
coverage report

# Gerar relatório HTML
coverage html
```

O relatório HTML será gerado na pasta `htmlcov/` e pode ser visualizado abrindo o arquivo `htmlcov/index.html` no navegador.

## Estrutura dos testes

Os testes estão organizados nas seguintes classes:

### Testes Principais (`tests.py`)
- **`AlunoModelTest`**: Testes para o modelo Aluno (validação de dados, cálculo de idade, unicidade)
- **`ProfessorModelTest`**: Testes para o modelo Professor (status ativo/inativo, métodos)
- **`EquipeModelTest`**: Testes para o modelo Equipe (status da equipe)
- **`TurmaModelTest`**: Testes para o modelo Turma (status ativa/inativa, relacionamentos)
- **`DisciplinaModelTest`**: Testes para o modelo Disciplina (status e métodos)
- **`AtendimentoModelTest`**: Testes para o modelo Atendimento (geração automática de códigos)
- **`AvaliacaoModelTest`**: Testes para o modelo Avaliacao (criação automática de notas)
- **`MediaCalculationTest`**: Testes para cálculos de médias (bimestral e final)
- **`RegistroUsuarioFormTest`**: Testes para formulário de registro de usuários
- **`TurmaFormTest`**: Testes para formulário de criação de turmas
- **`ViewsTest`**: Testes básicos para views (autenticação, acesso)
- **`ModelRelationshipTest`**: Testes de relacionamentos entre modelos

### Testes de Integração (`test_integration.py`)
- **`IntegrationTest`**: Testes de fluxos completos do sistema
- **`FormValidationTest`**: Testes adicionais de validação de formulários
- **`ModelMethodsTest`**: Testes para métodos específicos dos modelos
- **`EdgeCasesTest`**: Testes para casos extremos e edge cases

## Estatísticas dos Testes

- **Total de testes**: 29+ testes implementados
- **Cobertura**: Modelos, Forms, Views e relacionamentos
- **Tipos de teste**: Unitários, integração, validação e edge cases

### Comandos individuais
```bash
# Executar todos os testes
python manage.py test gestao_escolar

# Executar testes específicos
python manage.py test gestao_escolar.tests.AlunoModelTest

# Executar com cobertura (após instalar requirements-dev.txt)
coverage run --source='.' manage.py test gestao_escolar
coverage report  # Relatório em texto
coverage html    # Relatório HTML em htmlcov/index.html
```

## Resultados de Cobertura de Testes

**Cobertura Total: 60%**

| Arquivo | Linhas | Faltando | Cobertura |
|---------|---------|----------|-----------|
| **models.py** | 217 | 9 | **96%** |
| **settings.py** | 38 | 1 | **97%** |
| **templatetags/aluno_extras.py** | 9 | 2 | **78%** |
| **forms.py** | 67 | 18 | **73%** |
| **views.py** | 505 | 313 | **38%** |
| **Outros** | 26 | 0 | **100%** |

**Total de Testes:** 41 (29 unitários + 12 integração)
- ✅ **100% dos testes passando**
- ✅ **Cobertura excelente nos modelos** (96%)
- ⚠️ **Views precisam de mais testes** (38%)

### Visualizar Relatório HTML
Após executar `coverage html`, abra o arquivo:
```
htmlcov/index.html
```

# 🚀 CI/CD e Deploy

## Integração Contínua com Render

O projeto está configurado com **pipeline de CI/CD automatizado** utilizando o serviço [Render](https://dashboard.render.com/), proporcionando deploy automático e confiável.

### 🔄 Pipeline Automatizado

**Trigger de Deploy:**
- ✅ **Push automático**: Deploy disparado a cada push na branch `main`
- ✅ **Testes automatizados**: Execução da suíte de testes antes do deploy
- ✅ **Build automático**: Construção e preparação do ambiente de produção

### 📋 Processo de Deploy

1. **Commit & Push**: Desenvolvedores fazem push para a branch `main`
2. **Build Trigger**: Render detecta automaticamente as mudanças
3. **Execução de Testes**: Pipeline executa todos os 41 testes unitários e de integração
4. **Deploy Condicional**: Deploy só ocorre se todos os testes passarem ✅
5. **Ambiente Live**: Aplicação disponibilizada automaticamente

### 🌐 Ambientes

| Ambiente | Branch | URL | Status |
|----------|--------|-----|--------|
| **Produção** | `main` | [Em produção via Render] | 🟢 Ativo |
| **Desenvolvimento** | Local | `localhost:8000` | 🔧 Local |

### 🛡️ Benefícios do CI/CD

- **🔒 Qualidade garantida**: Não permite deploy com testes falhando
- **⚡ Deploy rápido**: Automatização reduz tempo de deploy
- **🔄 Rollback fácil**: Histórico de versões para reversão rápida
- **👥 Colaboração**: Equipe pode trabalhar simultaneamente com segurança
- **📊 Monitoramento**: Logs e métricas de deploy disponíveis no dashboard

### 📊 Monitoramento e Logs

**Via Dashboard Render:**
```bash
# Acesso aos logs em tempo real
Dashboard → Aplicação → Logs

# Métricas de performance
Dashboard → Aplicação → Metrics

# Histórico de deploys
Dashboard → Aplicação → Events
```

**Comandos para monitoramento local:**
```bash
# Verificar status dos testes
python manage.py test gestao_escolar --verbosity=2

# Monitorar cobertura
coverage run --source='.' manage.py test gestao_escolar
coverage report

# Verificar saúde da aplicação
python manage.py check --deploy
```

### 📁 Configuração

O projeto inclui os arquivos necessários para o Render:
- `requirements.txt` - Dependências de produção
- `Procfile` - Comandos de inicialização
- Configurações de ambiente via dashboard do Render

coverage report
coverage html


# Estrtutura do projeto

```bash
├── manage.py
|── README.md
├── gestao_escolar/
│   ├── __pycache__/
|   ├── migrations/
|   ├── static/
|   |    ├── css/
|   |        ├── style.css
|   |    ├── js/
|   |        ├── cep_autocomplete.js
|   ├── templates/
|   |    ├── ...
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   |── models.py
|   |── roles.py
|   |── testes.py
|   |── views.py
|
|── media/
|    ├── documentos/
|    |    |── alunos/
|    |    |── atendimentos/
|    |    |── equipe/
|    |    |── professores/
├── setup/
|   ├── __pycache__/
|   |   ├── ...
|   ├── __init__.py
|   ├── asgi.py
|   ├── settings.py
|   ├── urls.py
|   ├── wsgi.py
├── .gitignore
├── .env
```

# Agradecimentos

Agradecemos à orientadora do projeto, **Keyla Morales de Lima Garcia**, pela orientação e apoio durante o desenvolvimento do projeto.