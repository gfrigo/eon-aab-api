CREATE TABLE `SampleFiles` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `sample_id` int unsigned NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `file_type` varchar(50) NOT NULL,
  `storage_path` varchar(500) NOT NULL,
  `file_size` bigint NOT NULL,
  `checksum` varchar(64) NOT NULL,
  `uploaded_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),
  CONSTRAINT `fk_samplefiles_sample` FOREIGN KEY (`sample_id`)
    REFERENCES `Samples` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,

  INDEX `idx_sample_id` (`sample_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
