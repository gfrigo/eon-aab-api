CREATE TABLE usuarios (
  usr_id            CHAR(36)      NOT NULL,
  usr_email         VARCHAR(255)  NOT NULL,
  usr_senha_hash    VARCHAR(255)  NOT NULL,
  usr_nome_completo VARCHAR(150)  NOT NULL,
  usr_perfil        ENUM('analista','admin','visualizador') NOT NULL,
  usr_ativo         TINYINT(1)    NOT NULL DEFAULT 1,
  usr_criado_em     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  usr_atualizado_em DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
                                  ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT pk_usuarios  PRIMARY KEY (usr_id),
  CONSTRAINT uq_usr_email UNIQUE (usr_email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;