# 💻 Sistema de Gestão de Eventos Acadêmicos (SGEA)

![Status do Projeto](https://img.shields.io/badge/STATUS-CONCLUÍDO-GREEN?style=for-the-badge)

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
* **Database:** (A ser definido, ex: PostgreSQL, SQLite)
* **Frontend:** HTML/CSS (Inicialmente para prototipação)
* **Versionamento:** Git & GitHub

---

## ✨ Funcionalidades

O sistema SGEA oferece as seguintes funcionalidades principais:

1.  **Cadastro e Autenticação de Usuários:** Permite o cadastro e login de diferentes perfis (alunos, professores, organizadores).
2.  **Gerenciamento de Eventos (Organizadores):** Criação, edição e exclusão de eventos, incluindo dados como tipo, datas (inicial/final), horário, local e quantidade de participantes.
3.  **Inscrição em Eventos (Alunos e Professores):** Usuários cadastrados podem se inscrever nos eventos disponíveis, vinculando o evento ao seu perfil.
4.  **Emissão de Certificados (Organizadores):** Capacidade de emitir certificados para usuários devidamente inscritos em um evento.

---

## 🚀 Como Executar o Projeto

Para ter uma cópia local do projeto rodando para desenvolvimento e testes, siga os passos abaixo:

### 📋 Pré-requisitos

Você precisará ter instalado em sua máquina:

* **Python 3.x**
* **pip** (gerenciador de pacotes Python)

### ⚙️ Instalação (Backend)

1.  **Clone o repositório:**
    ```bash
    git clone [Link do seu repositório]
    cd nome-do-seu-repositorio
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # No Linux/macOS
    .\venv\Scripts\activate   # No Windows
    ```

3.  **Instale as dependências do projeto:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Crie o arquivo `requirements.txt` com `pip freeze > requirements.txt`)*

4.  **Configuração do Banco de Dados:**
    * Configure as variáveis de ambiente do seu banco de dados (ex: no arquivo `.env` ou em `settings.py`).
    * **Execute as migrações do Django:**
        ```bash
        python manage.py makemigrations
        python manage.py migrate
        ```
    *(Você também pode precisar criar um superusuário: `python manage.py createsuperuser`)*

5.  **Rode o servidor de desenvolvimento:**
    ```bash
    python manage.py runserver
    ```

6.  **Acesse a Aplicação:**
    Abra seu navegador e acesse: `http://127.0.0.1:8000/`

---

## 🖼️ Protótipo da Interface (Layout)

O layout das telas da aplicação pode ser visualizado no link abaixo:

* **Protótipo de Interface:** [Link para o Figma, Adobe XD ou diretório HTML/CSS inicial]

*(**Nota:** Para a entrega do projeto, o protótipo visual da interface é fornecido, mas nem todas as interfaces podem estar totalmente funcionais no código. O foco principal é a lógica **backend** e os **Modelos** do Django).*

---

## 🧩 Estrutura do Projeto e Documentação

O projeto está estruturado em aplicações (apps) do Django para organizar as funcionalidades e seguir as boas práticas.

* **Documento de Requisitos e Casos de Uso:** O detalhamento dos requisitos funcionais e os 5 casos de uso principais (Cadastro de Usuários, Cadastro de Eventos, Inscrição, Emissão de Certificados e Autenticação) está disponível no arquivo **`[caminho/para/documento-requisitos.pdf]`**.
* **Diagrama do Banco de Dados:** O diagrama lógico do banco e o script SQL estão no diretório **`[caminho/para/docs/]`**.

---

## 🤝 Contribuição (Opcional)

Sinta-se à vontade para contribuir! Se tiver sugestões ou quiser reportar bugs:

1.  Faça um **fork** do projeto.
2.  Crie uma nova **branch** (`git checkout -b feature/minha-feature`).
3.  Faça suas **alterações** e commite (`git commit -m 'feat: Adiciona nova funcionalidade X'`).
4.  Faça **push** para a branch (`git push origin feature/minha-feature`).
5.  Abra um **Pull Request (PR)**.

---

## 👨‍💻 Autor

| [<img src="[URL_SUA_FOTO]" width="100px;"/>](https://github.com/[SEU_GITHUB]) |
| :---: |
| **[Seu Nome Completo]** |
| [Seu LinkedIn ou Outro Contato] |

---

## ⚖️ Licença

Este projeto está sob a licença **[Nome da Licença, ex: MIT License]** - veja o arquivo `LICENSE.md` para mais detalhes.
