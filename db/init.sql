CREATE TABLE IF NOT EXISTS usuario (
	id INT PRIMARY KEY AUTO_INCREMENT,

	login VARCHAR(255) NOT NULL UNIQUE,
	senha VARCHAR(255) NOT NULL,

	nome_completo VARCHAR(255) NOT NULL,

	cargo ENUM('admin', 'atendente') DEFAULT 'atendente' NOT NULL
);

CREATE TABLE IF NOT EXISTS cliente (
	id INT PRIMARY KEY AUTO_INCREMENT,

	nome_completo VARCHAR(255) NOT NULL,
	cpf VARCHAR(11) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS quarto (
	id INT PRIMARY KEY AUTO_INCREMENT,

	codigo VARCHAR(4) NOT NULL UNIQUE,
	capacidade INT NOT NULL,
	valor DECIMAL(10, 2) NOT NULL,

	CONSTRAINT check_capacidade_positiva CHECK(capacidade > 0),
	CONSTRAINT check_valor_nao_negativo CHECK(valor >= 0)
);

CREATE TABLE IF NOT EXISTS reserva (
	id INT PRIMARY KEY AUTO_INCREMENT,

	quarto_id INT NOT NULL,
	usuario_id INT NOT NULL,
	cliente_id INT NOT NULL,

	data_checkin DATE NOT NULL,
	data_checkout DATE NOT NULL,

	status ENUM('pendente', 'confirmada', 'cancelada', 'finalizada') DEFAULT 'pendente' NOT NULL,

	FOREIGN KEY (quarto_id) REFERENCES quarto(id),
	FOREIGN KEY (usuario_id) REFERENCES usuario(id),
	FOREIGN KEY (cliente_id) REFERENCES cliente(id),

	CONSTRAINT check_checkin_menor_que_checkout CHECK(data_checkout > data_checkin)
);

INSERT IGNORE INTO usuario (login, senha, nome_completo, cargo)
VALUES ('admin', SHA2('admin123', 256), 'Administrador', 'admin');
