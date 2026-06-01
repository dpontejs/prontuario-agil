USE clinica_db;

INSERT INTO medico (nome, crm, especialidade) VALUES
('Dr. Carlos Silva', 'CRM-RN-1234', 'Cardiologia'),
('Dra. Ana Oliveira', 'CRM-RN-5678', 'Dermatologia'),
('Dr. Pedro Santos', 'CRM-RN-9012', 'Ortopedia'),
('Dra. Maria Costa', 'CRM-RN-3456', 'Pediatria'),
('Dr. João Ferreira', 'CRM-RN-7890', 'Clínica Geral');

INSERT INTO paciente (nome, cpf, email, telefone, data_nascimento) VALUES
('Lucas Almeida', '123.456.789-00', 'lucas@email.com', '(84) 99999-0001', '1990-05-15'),
('Fernanda Lima', '234.567.890-11', 'fernanda@email.com', '(84) 99999-0002', '1985-08-22'),
('Roberto Souza', '345.678.901-22', 'roberto@email.com', '(84) 99999-0003', '1978-12-03'),
('Juliana Martins', '456.789.012-33', 'juliana@email.com', '(84) 99999-0004', '1995-03-10'),
('André Pereira', '567.890.123-44', 'andre@email.com', '(84) 99999-0005', '2000-07-28');

INSERT INTO horario_disponivel (medico_id, data_hora, is_ocupado) VALUES
(1, '2025-06-02 09:00:00', TRUE),
(1, '2025-06-02 10:00:00', FALSE),
(2, '2025-06-02 14:00:00', TRUE),
(3, '2025-06-03 08:00:00', FALSE),
(4, '2025-06-03 15:00:00', TRUE),
(5, '2025-06-04 09:00:00', FALSE);

INSERT INTO agendamento (horario_id, paciente_id, status) VALUES
(1, 1, 'CONFIRMADO'),
(3, 2, 'RESERVADO'),
(5, 4, 'CONFIRMADO');

INSERT INTO prontuario (paciente_id, medico_id, notas_clinicas, diagnostico, prescricao, finalizado) VALUES
(1, 1, 'Paciente relata dores no peito há 3 dias.', 'Angina estável', 'AAS 100mg 1x ao dia', TRUE),
(2, 2, 'Lesão eritematosa no braço direito.', 'Dermatite de contato', 'Hidrocortisona creme 1%', FALSE);
