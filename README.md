# 💻 Sistema de Gestão de Eventos Acadêmicos (SGEA)

![Status do Projeto](https://img.shields.io/badge/STATUS-CONCLUÍDO-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/PYTHON-3.13.7-blue?style=for-the-badge)

---

## 📄 Sobre o Projeto

O **Sistema de Gestão de Eventos Acadêmicos (SGEA)** é uma aplicação web desenvolvida para gerenciar eventos como seminários, palestras, minicursos e semanas acadêmicas.

O foco do projeto está na **modelagem**, **backend em Django** e **estrutura de dados**, seguindo o padrão MVT e boas práticas de desenvolvimento.

### 🎯 Objetivos Principais

- Modelagem e estruturação completa do projeto (apps, models, urls).
- Criação de modelos robustos e integração com banco de dados.
- Desenvolvimento da lógica backend para as funcionalidades centrais.
- Prototipação da interface (HTML/CSS).

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python + Django  
- **Banco de Dados:** SQLite  
- **Frontend:** HTML / CSS  
- **Versionamento:** Git & GitHub  

---

## ✨ Funcionalidades

1. **Cadastro e Autenticação de Usuários** (Alunos, Professores, Organizadores)  
2. **Gestão de Eventos (Organizadores)** — criar, editar e excluir eventos  
3. **Inscrição em Eventos (Participantes)**  
4. **Emissão de Certificados** para usuários inscritos  

---

## 🚀 Guia de Instalação e Execução

### 🔧 Pré-requisitos
- Python **3.13+**
- Git

---

### 📝 Passo a Passo

#### 1️⃣ Clonar o repositório
```bash
git clone https://github.com/brnd1206/sistema-de-gestao.git
cd sistema-de-gestao/Sgea
```

#### 2️⃣ Criar e ativar ambiente virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / Mac
python3 -m venv venv
source venv/bin/activate
```

#### 3️⃣ Instalar dependências
```bash
pip install django djangorestframework pillow python-dotenv
```

#### 4️⃣ Configurar Variáveis de Ambiente (.env)
O sistema utiliza variáveis de ambiente para o envio de e-mails.

* **Modo Desenvolvimento (Sem E-mail Real):** Se você não criar o arquivo `.env`, o sistema detectará automaticamente e imprimirá os links de ativação de conta no **terminal/console** onde o servidor estiver rodando.
* **Modo Produção (Com E-mail Real):** Para que os e-mails sejam enviados via Gmail:
    1. Crie um arquivo chamado `.env` na pasta raiz (junto com o `manage.py`).
    2. Adicione manualmente no `.env`:
    ```env
    EMAIL_USER=seu_email@gmail.com
    EMAIL_PASSWORD=sua_senha_de_app_gerada_no_google
    ```
    > **Nota:** A senha deve ser uma "Senha de App" gerada nas configurações de segurança da sua conta Google, e não a sua senha de login habitual.

#### 5️⃣ Criar as tabelas do banco (caso não esteja criado)
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 6️⃣ Executar o servidor
```bash
python manage.py runserver
```

---

## 🧪 Guia de Testes e Massa de Dados

### 🔑 Credenciais de Teste

Utilize os usuários abaixo para validar as funcionalidades de cada perfil:

| Perfil | Usuário | Senha | Nível de Acesso |
| :--- | :--- | :--- | :--- |
| **Aluno** | `aluno` | `Aluno@123` | Inscrição em eventos, visualização de certificados. |
| **Professor** | `professor` | `Professor@123` | Visualização de eventos sob sua responsabilidade. |
| **Admin** | `admin` | `Admin@123` | **Superusuário**. Acesso total ao painel do organizador e admin do Django. |

### 1️⃣ Criar superusuário
```bash
python manage.py createsuperuser
```
Siga as instruções para criar o usuário organizador.

---

### 2️⃣ Roteiro de Testes Funcionais

#### **Cenário A — Organizador**
- Faça login como superusuário.
- Acesse o painel do organizador.
- Crie um evento e teste:
  - Upload de imagem (banner)
  - Máscara de data/hora
  - Listagem após salvar

#### **Cenário B — Participante**
- Crie uma conta com perfil **Aluno**.
- Abra o painel do participante.
- Acesse os detalhes do evento criado.
- Clique em **Inscrever-se**.

#### **Cenário C — API REST**

**Obter token de autenticação**
```json
POST /api/token-auth/
{
  "username": "seu_user",
  "password": "sua_senha"
}
```

**Listar eventos**
```
GET /api/eventos/
Authorization: Token SEU_TOKEN
```

**Inscrever via API**
```json
POST /api/inscrever/
Authorization: Token SEU_TOKEN
{
  "evento": 1
}
```

---

## 📖 Casos de Uso

### 🟦 1. Casos de Acesso

| ID | Caso de Uso | Ator | Objetivo |
|----|-------------|------|----------|
| **CU01** | Cadastrar Usuário | Aluno / Professor / Organizador | Criar conta e definir perfil |
| **CU02** | Autenticar-se | Todos | Login seguro no sistema |

---

### 🟩 2. Usuário Comum (Aluno / Professor)

| ID | Caso de Uso | Ator | Objetivo |
|----|-------------|------|----------|
| **CU03** | Visualizar Eventos | Aluno / Professor | Ver lista de eventos |
| **CU04** | Consultar Detalhes | Aluno / Professor | Ver informações completas |
| **CU05** | Inscrever-se | Aluno / Professor | Registrar inscrição |
| **CU06** | Baixar Certificado | Aluno / Professor | Emitir certificado |

---

### 🟥 3. Organizador

| ID | Caso de Uso | Ator | Objetivo |
|----|-------------|------|----------|
| **CU07** | Criar Evento | Organizador | Cadastrar novos eventos |
| **CU08** | Editar Evento | Organizador | Alterar informações |
| **CU09** | Excluir Evento | Organizador | Remover evento e inscrições |
| **CU10** | Gerenciar Participantes | Organizador | Ver e controlar inscritos |
| **CU11** | Emitir Certificados | Organizador | Gerar certificados |

---

## 🤝 Contribuição

Fique à vontade para abrir issues, enviar pull requests ou sugerir novas funcionalidades!

---

## 👨‍💻 Autores

| Nome | Perfil |
|------|--------|
| **Bernardo de Carvalho Leite** | https://www.linkedin.com/in/bernardo-de-carvalho-leite-4a509a323/ |
| **Bernardo dos Santos Gomes** | https://github.com/bernardosgomes |

---
