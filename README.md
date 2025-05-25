# Software de Gestão Escolar

Software com framework web e script web (JavaScript), com uso de API, banco de dados em nuvenm, acessibilidade, teste e controle de versão para ferramenta digital de gestão escolar desenvolvido para a disciplina de Projeto Integrador para os cursos de Bacharelado em Tecnologia da Informação Ciência de Dados e Engenharia da Computação da Universidade Virtual do Estado de São Paulo.

# Equipe de Desenvolvimento

UNIVERSIDADE VIRTUAL DO ESTADO DE SÃO PAULO

* [Bruna Michelle Sargenti Moreira](https://github.com/BrunaMoreira100)
* [Diego Nespolon Bertazzoli](https://github.com/diegobertazzoli)
* [Elson Atushi Kondo](https://github.com/EAKUNIVESP)
* [Fabiana Santos Lima Sugamele](https://github.com/fabianasugamele)
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

# Estrtutura do projeto

``` bash
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

Agradecemos ao orientador do projeto, Lucas Silva Pamio, pela orientação e apoio durante o desenvolvimento do projeto.
