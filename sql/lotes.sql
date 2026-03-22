CREATE TABLE lotes (
  lot_id             CHAR(36)    NOT NULL,
  lot_criado_por     CHAR(36)    NOT NULL,
  lot_codigo         VARCHAR(20) NOT NULL,
  lot_total_amostras INT         NOT NULL DEFAULT 0,
  lot_qtd_tier1      INT         NOT NULL DEFAULT 0,
  lot_qtd_tier2      INT         NOT NULL DEFAULT 0,
  lot_qtd_tier3      INT         NOT NULL DEFAULT 0,
  lot_criado_em      DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT pk_lotes          PRIMARY KEY (lot_id),
  CONSTRAINT uq_lot_codigo     UNIQUE (lot_codigo),
  CONSTRAINT fk_lot_criado_por FOREIGN KEY (lot_criado_por)
    REFERENCES usuarios (usr_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;