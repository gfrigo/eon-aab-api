CREATE TABLE administradores (
  adm_id           CHAR(36)     NOT NULL,
  adm_usr_id       CHAR(36)     NOT NULL,
  adm_departamento VARCHAR(100) NOT NULL,
  adm_nivel_acesso VARCHAR(50)  NOT NULL,
  adm_criado_em    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT pk_administradores PRIMARY KEY (adm_id),
  CONSTRAINT uq_adm_usr_id      UNIQUE (adm_usr_id),
  CONSTRAINT fk_adm_usr         FOREIGN KEY (adm_usr_id)
    REFERENCES usuarios (usr_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;