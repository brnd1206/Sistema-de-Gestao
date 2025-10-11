
-- =================================================================
-- SCRIPT DE CRIAÇÃO DO BANCO DE DADOS PARA O SISTEMA DE EVENTOS
-- =================================================================

CREATE TABLE usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME NULL,
    is_superuser BOOLEAN NOT NULL,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    date_joined DATETIME NOT NULL,
    telefone VARCHAR(15) NOT NULL,
    instituicao_ensino VARCHAR(255) NOT NULL,
    perfil VARCHAR(15) NOT NULL
);

CREATE TABLE auth_group (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE auth_permission (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type_id INTEGER NOT NULL,
    codename VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    UNIQUE (content_type_id, codename)
);

CREATE TABLE evento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(200) NOT NULL,
    tipo_evento VARCHAR(50) NOT NULL,
    data_inicio DATETIME NOT NULL,
    data_fim DATETIME NOT NULL,
    local VARCHAR(255) NOT NULL,
    quantidade_participantes INTEGER UNSIGNED NOT NULL CHECK (quantidade_participantes >= 0),
    data_criacao DATETIME NOT NULL,
    data_atualizacao DATETIME NOT NULL,
    organizador_id BIGINT NOT NULL,
    FOREIGN KEY (organizador_id) REFERENCES usuario(id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE inscricao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_inscricao DATETIME NOT NULL,
    usuario_id BIGINT NOT NULL,
    evento_id BIGINT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) DEFERRABLE INITIALLY DEFERRED,
    FOREIGN KEY (evento_id) REFERENCES evento(id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE certificado (
    inscricao_id BIGINT PRIMARY KEY,
    codigo_validacao VARCHAR(50) NOT NULL UNIQUE,
    data_emissao DATETIME NOT NULL,
    FOREIGN KEY (inscricao_id) REFERENCES inscricao(id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE usuario_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id BIGINT NOT NULL,
    group_id INTEGER NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) DEFERRABLE INITIALLY DEFERRED,
    FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED,
    UNIQUE (usuario_id, group_id)
);

CREATE TABLE usuario_user_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id BIGINT NOT NULL,
    permission_id INTEGER NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) DEFERRABLE INITIALLY DEFERRED,
    FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED,
    UNIQUE (usuario_id, permission_id)
);

CREATE TABLE auth_group_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED,
    FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED,
    UNIQUE (group_id, permission_id)
);
