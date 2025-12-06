# 💻 Sistema de Gestão de Eventos Acadêmicos (SGEA)

![Status do Projeto](https://img.shields.io/badge/STATUS-CONCLUÍDO-blue?style=for-the-badge) ![Python](https://img.shields.io/badge/PYTHON-3.13.7-blue?style=for-the-badge)

---

## 📄 Sobre o Projeto

O **Sistema de Gestão de Eventos Acadêmicos (SGEA)** é uma aplicação web desenvolvida para permitir o gerenciamento completo de eventos como seminários, palestras, minicursos e semanas acadêmicas.

O foco principal deste projeto está na **modelagem do sistema, arquitetura backend (Django)** e na criação dos modelos de dados, seguindo o padrão MVC/MVT (Model-View-Template) e aplicando boas práticas de desenvolvimento.

### Objetivos Principais

* Modelagem e estruturação completa do projeto Django (apps, models, urls) com base nos requisitos funcionais e não funcionais.
* Construção de modelos de dados robustos e integração com o banco de dados.
* Criação da lógica backend para as funcionalidades principais.
* Prototipação da interface de usuário (front-end).

---

## 🛠️ Tecnologias Utilizadas

Este projeto foi construído utilizando as seguintes tecnologias:

* **Backend Framework:** Python (com Django)
* **Database:** SQLite
* **Frontend:** HTML/CSS
* **Versionamento:** Git & GitHub

---

## ✨ Funcionalidades

O sistema SGEA oferece as seguintes funcionalidades principais:

1.  **Cadastro e Autenticação de Usuários:** Permite o cadastro e login de diferentes perfis (alunos, professores, organizadores).
2.  **Gerenciamento de Eventos (Organizadores):** Criação, edição e exclusão de eventos, incluindo dados como tipo, datas (inicial/final), horário, local e quantidade de participantes.
3.  **Inscrição em Eventos (Alunos e Professores):** Usuários cadastrados podem se inscrever nos eventos disponíveis, vinculando o evento ao seu perfil.
4.  **Emissão de Certificados (Organizadores):** Capacidade de emitir certificados para usuários devidamente inscritos em um evento.

---

## 🚀 Guia de Instalação e Execução

Siga os passos abaixo para configurar o ambiente de desenvolvimento e executar o projeto em sua máquina local.

### Pré-requisitos
* **Python 3.13+** instalado.
* **Git** instalado.

### Passo a Passo

1. **Clone o repositório**
   ```bash
   git clone https://github.com/brnd1206/sistema-de-gestao.git
   cd sistema-de-gestao/Sgea

2. **Crie e ative um ambiente virtual**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux / Mac
   python3 -m venv venv
   source venv/bin/activate

3. **Instale as dependências Execute o comando abaixo para instalar o Django, DRF e Pillow**
   ```bash
   pip install django pillow djangorestframework

4. **Realize as migrações do banco de dados Crie as tabelas necessárias no SQLite**
   ```bash
   python manage.py makemigrations
   python manage.py migrate

5. **Execute o servidor local**
   ```bash
   python manage.py runserver
   
---

🧪 Guia de Testes e Massa de Dados
Para testar as funcionalidades do sistema, recomenda-se popular o banco de dados com dados iniciais seguindo o roteiro abaixo.

1. Criando um Superusuário (Organizador Principal)
Para acessar todas as funções administrativas e criar os primeiros eventos, é necessário um superusuário. No terminal, execute:
   ```bash
   python manage.py createsuperuser

Siga as instruções para definir usuário, email e senha. Este usuário terá permissões de Organizador.

2. Roteiro de Testes Funcionais
Cenário A: Organizador (Gestão de Eventos)

Faça login com o superusuário criado (ou crie um novo usuário e defina o perfil como "Organizador").

Acesse o Dashboard do Organizador.

Clique em "Criar Novo Evento".

Preencha o formulário:

Teste o upload de uma imagem (Banner).

Verifique a máscara de data/hora nos campos.

Salve e verifique se o evento aparece na lista com as datas de início e fim corretas.

Cenário B: Participante (Inscrição)

Abra uma guia anônima ou faça logout.

Acesse a página de Cadastro e crie uma conta com perfil "Aluno".

No Dashboard do Participante, localize o evento criado no Cenário A.

Clique no botão azul "Detalhes". Verifique se o banner é exibido corretamente.

Clique em "Inscrever-se". O evento deve mover para a lista "Meus Eventos Inscritos".

Cenário C: Teste da API REST Utilize o Postman ou Insomnia para testar os endpoints:

Obter Token (Login):

POST /api/token-auth/

Body: {"username": "seu_user", "password": "sua_senha"}

Copie o "token" retornado.

Listar Eventos:

GET /api/eventos/

Header: Authorization: Token SEU_TOKEN_COPIADO

Inscrever-se via API:

POST /api/inscrever/

Header: Authorization: Token SEU_TOKEN_COPIADO

Body: {"evento": 1}

---

## 📖 Casos de Usos

### 1. Casos de Uso de Acesso

| ID | Caso de Uso | Ator Principal | Objetivo |
|----|-------------|----------------|----------|
| **CU01** | **Cadastrar Usuário** | Usuário (Aluno, Professor, Organizador) | Permitir que um novo usuário crie uma conta, definindo seu perfil de acesso ao sistema (Aluno, Professor ou Organizador). |
| **CU02** | **Autenticar-se (Login)** | Usuário (Qualquer Perfil) | Permitir que o usuário acesse o sistema de forma segura, validando suas credenciais de login e senha. |

---

### 2. Casos de Uso do Usuário Comum (Aluno / Professor)

Estes casos de uso são focados na interação do público-alvo com os eventos.

| ID | Caso de Uso | Ator Principal | Objetivo |
|----|-------------|----------------|----------|
| **CU03** | **Visualizar Lista de Eventos** | Usuário (Aluno/Professor) | Exibir a lista completa de eventos acadêmicos disponíveis, com informações básicas como nome, tipo e data. |
| **CU04** | **Consultar Detalhes do Evento** | Usuário (Aluno/Professor) | Exibir informações detalhadas de um evento específico, como local, horário, palestrantes e ementa. |
| **CU05** | **Realizar Inscrição em Evento** | Usuário (Aluno/Professor) | Permitir que o usuário se inscreva em um evento, vinculando-o ao seu perfil e gerando um comprovante de inscrição. |
| **CU06** | **Obter Certificado de Participação** | Usuário (Aluno/Professor) | Permitir que o usuário devidamente inscrito e com presença registrada baixe o certificado referente ao evento concluído. |

---

### 3. Casos de Uso do Organizador

Estes casos de uso são focados na gestão e administração dos eventos no sistema.

| ID | Caso de Uso | Ator Principal | Objetivo |
|----|-------------|----------------|----------|
| **CU07** | **Criar Novo Evento** | Organizador | Inserir um novo evento no sistema, definindo dados como tipo (seminário, palestra, minicurso), datas (inicial/final), horário, local e limite de participantes. |
| **CU08** | **Editar Dados do Evento** | Organizador | Modificar as informações de um evento já cadastrado (exceto após o início, dependendo das regras de negócio). |
| **CU09** | **Excluir Evento** | Organizador | Remover um evento do sistema, cancelando todas as inscrições relacionadas. |
| **CU10** | **Gerenciar Participantes/Inscrições** | Organizador | Visualizar a lista de usuários inscritos em um evento específico e gerenciar o status de presença. |
| **CU11** | **Emitir Certificados para Participantes** | Organizador | Gerar e disponibilizar os certificados para todos os usuários que cumpriram os requisitos de participação no evento. |

---

## 🤝 Contribuição

Sinta-se à vontade para contribuir! Se tiver sugestões ou quiser reportar bugs.

---

## 👨‍💻 Autores

| **Bernardo de Carvalho Leite** |
| https://www.linkedin.com/in/bernardo-de-carvalho-leite-4a509a323/ |

| **Bernardo dos Santos Gomes** |
| https://github.com/bernardosgomes |
