CREATE TABLE amostras (
  ams_id            CHAR(36)    NOT NULL,
  ams_codigo        VARCHAR(20) NOT NULL,
  ams_criado_por    CHAR(36)    NOT NULL,
  ams_analisado_por CHAR(36)    NULL,
  ams_tier          TINYINT     NULL CHECK (ams_tier IN (1, 2, 3)),
  ams_tier_label    VARCHAR(20) NULL,
  ams_status        ENUM('pendente','processando','concluido','rejeitado')
                                NOT NULL DEFAULT 'pendente',
  ams_coletado_em   DATETIME    NOT NULL,
  ams_analisado_em  DATETIME    NULL,
  ams_criado_em     DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT pk_amostras          PRIMARY KEY (ams_id),
  CONSTRAINT uq_ams_codigo        UNIQUE (ams_codigo),
  CONSTRAINT fk_ams_criado_por    FOREIGN KEY (ams_criado_por)
    REFERENCES usuarios (usr_id) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_ams_analisado_por FOREIGN KEY (ams_analisado_por)
    REFERENCES usuarios (usr_id) ON DELETE SET NULL ON UPDATE CASCADE,

  INDEX idx_ams_status     (ams_status),
  INDEX idx_ams_tier       (ams_tier),
  INDEX idx_ams_criado_em  (ams_criado_em)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;