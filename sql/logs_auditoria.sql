CREATE TABLE logs_auditoria (
  log_id            CHAR(36)     NOT NULL,
  log_usr_id        CHAR(36)     NULL,
  log_acao          VARCHAR(100) NOT NULL,
  log_tipo_entidade VARCHAR(50)  NOT NULL,
  log_entidade_id   CHAR(36)     NULL,
  log_metadados     JSON         NULL,
  log_criado_em     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT pk_logs_auditoria PRIMARY KEY (log_id),
  CONSTRAINT fk_log_usr        FOREIGN KEY (log_usr_id)
    REFERENCES usuarios (usr_id) ON DELETE SET NULL ON UPDATE CASCADE,

  INDEX idx_log_usr_id         (log_usr_id),
  INDEX idx_log_tipo_entidade  (log_tipo_entidade),
  INDEX idx_log_criado_em      (log_criado_em)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;