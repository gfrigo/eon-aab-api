CREATE TABLE `BatchItems` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `batch_id` int unsigned NOT NULL,
  `sample_id` int unsigned NOT NULL,

  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_batch_sample` (`batch_id`, `sample_id`),
  CONSTRAINT `fk_batchitems_batch` FOREIGN KEY (`batch_id`)
    REFERENCES `Batches` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_batchitems_sample` FOREIGN KEY (`sample_id`)
    REFERENCES `Samples` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;