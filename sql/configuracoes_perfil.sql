CREATE TABLE configuracoes_perfil (
  prf_id               CHAR(36)    NOT NULL,
  prf_usr_id           CHAR(36)    NOT NULL,
  prf_idioma           VARCHAR(10) NOT NULL DEFAULT 'pt-BR',
  prf_fuso_horario     VARCHAR(50) NOT NULL DEFAULT 'America/Sao_Paulo',
  prf_pref_notificacao VARCHAR(20) NOT NULL DEFAULT 'email',
  prf_preferencias_ui  JSON        NULL,
  prf_atualizado_em    DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP
                                   ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT pk_configuracoes_perfil PRIMARY KEY (prf_id),
  CONSTRAINT uq_prf_usr_id           UNIQUE (prf_usr_id),
  CONSTRAINT fk_prf_usr              FOREIGN KEY (prf_usr_id)
    REFERENCES usuarios (usr_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;