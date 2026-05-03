CREATE TABLE `Samples` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `batch_id` int unsigned NOT NULL,
  `code` varchar(20) NOT NULL,
  `created_by` int unsigned NOT NULL,
  `tier` tinyint NULL CHECK (`tier` IN (1, 2, 3)),
  `tier_label` varchar(20) NULL,
  `status` enum('pendente','processando','concluido','rejeitado') NOT NULL DEFAULT 'pendente',
  `collected_at` datetime NOT NULL,
  `analyzed_at` datetime NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_code` (`code`),
  CONSTRAINT `fk_samples_batch` FOREIGN KEY (`batch_id`)
    REFERENCES `Batches` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_samples_created_by` FOREIGN KEY (`created_by`)
    REFERENCES `Users` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,

  INDEX `idx_batch_id` (`batch_id`),
  INDEX `idx_status` (`status`),
  INDEX `idx_tier` (`tier`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;