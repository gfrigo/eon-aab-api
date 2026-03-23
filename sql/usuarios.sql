create table `ABS_Users` (
  `id` int unsigned not null auto_increment,
  `email` VARCHAR(50) not null,
  `password` VARCHAR(255) not null,
  `full_name` VARCHAR(100) not null,
  `profile` ENUM('admin', 'analista', 'visualizador') not null,
  `is_active` INTEGER not null,
  `created_at` DATETIME not null,
  `updated_at` DATETIME not null,
  primary key (`id`)
);