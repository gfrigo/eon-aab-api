create table `Users` (
  `id` int unsigned not null auto_increment,
  `email` VARCHAR(50) not null,
  `password` VARCHAR(255) not null,
  `full_name` VARCHAR(100) not null,
  `profile` ENUM('admin', 'analista', 'visualizador', 'dispositivo') not null,
  `is_active` INTEGER not null,
  `api_token` VARCHAR(255) NULL,
  `created_at` DATETIME not null,
  `updated_at` DATETIME not null,
  primary key (`id`)
);