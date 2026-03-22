CREATE TABLE itens_lote (
  itl_id     CHAR(36) NOT NULL,
  itl_lot_id CHAR(36) NOT NULL,
  itl_ams_id CHAR(36) NOT NULL,

  CONSTRAINT pk_itens_lote  PRIMARY KEY (itl_id),
  CONSTRAINT uq_itl_lot_ams UNIQUE (itl_lot_id, itl_ams_id),
  CONSTRAINT fk_itl_lot     FOREIGN KEY (itl_lot_id)
    REFERENCES lotes   (lot_id)  ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_itl_ams     FOREIGN KEY (itl_ams_id)
    REFERENCES amostras (ams_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;