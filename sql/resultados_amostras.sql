CREATE TABLE `SampleResults` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `sample_id` int unsigned NOT NULL,
  `image_path` varchar(500) NOT NULL,
  `confidence_score` float NOT NULL CHECK (`confidence_score` BETWEEN 0.0 AND 1.0),
  `ml_raw_output` json NOT NULL,
  `model_version` varchar(50) NOT NULL,
  `processed_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_sample_id` (`sample_id`),
  CONSTRAINT `fk_sampleresults_sample` FOREIGN KEY (`sample_id`)
    REFERENCES `Samples` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,

  INDEX `idx_model_version` (`model_version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;