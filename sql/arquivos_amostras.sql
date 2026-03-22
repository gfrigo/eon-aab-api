CREATE TABLE arquivos_amostras (
  arq_id              CHAR(36)     NOT NULL,
  arq_ams_id          CHAR(36)     NOT NULL,
  arq_nome            VARCHAR(255) NOT NULL,
  arq_tipo            VARCHAR(50)  NOT NULL,
  arq_caminho_storage VARCHAR(500) NOT NULL,
  arq_tamanho_bytes   BIGINT       NOT NULL,
  arq_checksum        VARCHAR(64)  NOT NULL,
  arq_enviado_em      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT pk_arquivos_amostras PRIMARY KEY (arq_id),
  CONSTRAINT fk_arq_ams           FOREIGN KEY (arq_ams_id)
    REFERENCES amostras (ams_id) ON DELETE CASCADE ON UPDATE CASCADE,

  INDEX idx_arq_ams_id (arq_ams_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;