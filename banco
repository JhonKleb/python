--DROP TABLE IF EXISTS denuncia CASCADE;
--DROP TABLE IF EXISTS patrimonio CASCADE;
--DROP TABLE IF EXISTS login_aluno CASCADE;
--DROP TABLE IF EXISTS login_servidor CASCADE;
--DROP TABLE IF EXISTS aluno CASCADE;
--DROP TABLE IF EXISTS servidor CASCADE;

CREATE TABLE aluno (
    matricula_al BIGINT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    turma VARCHAR(50)
);

CREATE TABLE servidor (
    matricula_serv BIGINT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE
);

CREATE TABLE login_aluno (
    id_login SERIAL PRIMARY KEY,
    matricula_al BIGINT NOT NULL,
    senha VARCHAR(255) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_login_al FOREIGN KEY (matricula_al)
        REFERENCES aluno(matricula_al)
        ON DELETE CASCADE
);

CREATE TABLE login_servidor (
    id_login SERIAL PRIMARY KEY,
    matricula_serv BIGINT NOT NULL,
    senha VARCHAR(255) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_login_serv FOREIGN KEY (matricula_serv)
        REFERENCES servidor(matricula_serv)
        ON DELETE CASCADE
);

CREATE TABLE patrimonio (
    tombo BIGINT PRIMARY KEY,
    descricao VARCHAR(255) NOT NULL,
    situacao VARCHAR(50) DEFAULT 'Em funcionamento',
    data_registro DATE DEFAULT CURRENT_DATE,
    local VARCHAR(100) NOT NULL,
    codigo VARCHAR(20) UNIQUE NOT NULL
);

CREATE TABLE denuncia (
    id_denuncia SERIAL PRIMARY KEY,
    tombo BIGINT, -- 🔹 Agora opcional
    matricula_al BIGINT NOT NULL,
    descricao TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'Aberta',
    data_denuncia TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    localizacao VARCHAR(100),
    CONSTRAINT fk_denuncia_al FOREIGN KEY (matricula_al)
        REFERENCES aluno(matricula_al)
        ON DELETE CASCADE
);

INSERT INTO servidor (matricula_serv, nome, email)
VALUES (242543, 'ServidorEx', 'servex@gmail.com');

INSERT INTO patrimonio (tombo, descricao, situacao, local, codigo) 
VALUES (4569, 'Projetor Epson', 'Em funcionamento', 'Laboratório 01', 'ABC12345');

INSERT INTO aluno (matricula_al, nome, email, turma) 
VALUES (2023120230020, 'Jhon Kleber Silva Costa', 'jhonklebersilvacosta0@gmail.com', 'INFO3A');

INSERT INTO denuncia (tombo, matricula_al, descricao, localizacao) 
VALUES (443215, 2023120230020, 'Equipamento sem algumas teclas', 'Laboratório 01');

INSERT INTO login_aluno (matricula_al, senha)
VALUES (2023120230020, 'senha_hash_aluno');

INSERT INTO login_servidor (matricula_serv, senha)
VALUES (242543, 'senha_hash_servidor');
