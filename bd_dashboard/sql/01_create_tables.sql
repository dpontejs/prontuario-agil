CREATE DATABASE IF NOT EXISTS clinica_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE clinica_db;

-- Espelha o model Medico do Prontuário Ágil (Django)
CREATE TABLE IF NOT EXISTS medico (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    crm VARCHAR(20) UNIQUE NOT NULL,
    especialidade VARCHAR(50) NOT NULL
);

-- Adição planejada no MVP do Prontuário Ágil
CREATE TABLE IF NOT EXISTS paciente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(14) UNIQUE NOT NULL,
    email VARCHAR(100),
    telefone VARCHAR(20),
    data_nascimento DATE
);

-- Espelha o model HorarioDisponivel do Prontuário Ágil
CREATE TABLE IF NOT EXISTS horario_disponivel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    medico_id INT NOT NULL,
    data_hora DATETIME NOT NULL,
    is_ocupado BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (medico_id) REFERENCES medico(id) ON DELETE CASCADE
);

-- Espelha o model Agendamento do Prontuário Ágil
-- paciente_id referencia a tabela paciente (evolução do IntegerField do Django)
CREATE TABLE IF NOT EXISTS agendamento (
    id INT AUTO_INCREMENT PRIMARY KEY,
    horario_id INT NOT NULL,
    paciente_id INT NOT NULL,
    status VARCHAR(20) DEFAULT 'RESERVADO',
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (horario_id) REFERENCES horario_disponivel(id) ON DELETE CASCADE,
    FOREIGN KEY (paciente_id) REFERENCES paciente(id) ON DELETE CASCADE
);

-- Adição planejada no MVP do Prontuário Ágil
CREATE TABLE IF NOT EXISTS prontuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paciente_id INT NOT NULL,
    medico_id INT NOT NULL,
    notas_clinicas TEXT,
    diagnostico TEXT,
    prescricao TEXT,
    data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    finalizado BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (paciente_id) REFERENCES paciente(id) ON DELETE CASCADE,
    FOREIGN KEY (medico_id) REFERENCES medico(id) ON DELETE CASCADE
);

-- Dados públicos CNES
CREATE TABLE IF NOT EXISTS estabelecimento_cnes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cnes_codigo VARCHAR(20),
    nome_fantasia VARCHAR(200),
    tipo_estabelecimento VARCHAR(100),
    uf CHAR(2),
    municipio VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS profissional_cnes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    estabelecimento_cnes_id INT,
    nome VARCHAR(200),
    cbo VARCHAR(100),
    carga_horaria INT,
    FOREIGN KEY (estabelecimento_cnes_id) REFERENCES estabelecimento_cnes(id) ON DELETE SET NULL
);
