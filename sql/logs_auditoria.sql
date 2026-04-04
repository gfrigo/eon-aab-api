CREATE TABLE `AuditLogs` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int unsigned NULL,
  `action` varchar(100) NOT NULL,
  `entity_type` varchar(50) NOT NULL,
  `entity_id` int unsigned NULL,
  `metadata` json NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),
  CONSTRAINT `fk_auditlogs_user` FOREIGN KEY (`user_id`)
    REFERENCES `Users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,

  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_entity_type` (`entity_type`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;