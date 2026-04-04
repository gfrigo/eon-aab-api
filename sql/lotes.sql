CREATE TABLE `Batches` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int unsigned NOT NULL,
  `code` varchar(20) NOT NULL,
  `total_samples` int NOT NULL DEFAULT 0,
  `tier1_count` int NOT NULL DEFAULT 0,
  `tier2_count` int NOT NULL DEFAULT 0,
  `tier3_count` int NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_code` (`code`),
  CONSTRAINT `fk_batches_user` FOREIGN KEY (`user_id`)
    REFERENCES `Users` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;