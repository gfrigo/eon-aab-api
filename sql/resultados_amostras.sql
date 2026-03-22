CREATE TABLE resultados_amostras (
  res_id             CHAR(36)    NOT NULL,
  res_ams_id         CHAR(36)    NOT NULL,
  res_pont_confianca FLOAT       NOT NULL
    CHECK (res_pont_confianca BETWEEN 0.0 AND 1.0),
  res_saida_bruta_ml JSON        NOT NULL,
  res_versao_modelo  VARCHAR(50) NOT NULL,
  res_processado_em  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT pk_resultados_amostras PRIMARY KEY (res_id),
  CONSTRAINT uq_res_ams_id          UNIQUE (res_ams_id),
  CONSTRAINT fk_res_ams             FOREIGN KEY (res_ams_id)
    REFERENCES amostras (ams_id) ON DELETE CASCADE ON UPDATE CASCADE,

  INDEX idx_res_versao_modelo (res_versao_modelo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;