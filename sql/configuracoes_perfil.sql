CREATE TABLE `ProfileSettings` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int unsigned NOT NULL,
  `language` varchar(10) NOT NULL DEFAULT 'pt-BR',
  `timezone` varchar(50) NOT NULL DEFAULT 'America/Sao_Paulo',
  `notification_pref` varchar(20) NOT NULL DEFAULT 'email',
  `ui_preferences` json NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_user_id` (`user_id`),
  CONSTRAINT `fk_profilesettings_user` FOREIGN KEY (`user_id`)
    REFERENCES `Users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;