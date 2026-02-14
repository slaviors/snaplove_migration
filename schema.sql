-- MySQL Schema for Snaplove Database Migration
-- Generated from MongoDB Mongoose Models
-- Date: 2026-02-15

-- Drop tables if they exist (in correct order to handle foreign keys)
DROP TABLE IF EXISTS `notifications`;
DROP TABLE IF EXISTS `broadcasts`;
DROP TABLE IF EXISTS `aiphotobooth_usages`;
DROP TABLE IF EXISTS `photo_collab_stickers`;
DROP TABLE IF EXISTS `photo_collabs`;
DROP TABLE IF EXISTS `photos`;
DROP TABLE IF EXISTS `reports`;
DROP TABLE IF EXISTS `tickets`;
DROP TABLE IF EXISTS `frame_likes`;
DROP TABLE IF EXISTS `frame_uses`;
DROP TABLE IF EXISTS `frame_tags`;
DROP TABLE IF EXISTS `frames`;
DROP TABLE IF EXISTS `follows`;
DROP TABLE IF EXISTS `maintenances`;
DROP TABLE IF EXISTS `users`;

-- Users Table
CREATE TABLE `users` (
  `id` VARCHAR(24) PRIMARY KEY,
  `image_profile` TEXT,
  `custom_profile_image` TEXT,
  `use_google_profile` BOOLEAN DEFAULT TRUE,
  `name` VARCHAR(100) NOT NULL,
  `username` VARCHAR(100) NOT NULL UNIQUE,
  `email` VARCHAR(255) NOT NULL UNIQUE,
  `password` TEXT,
  `role` ENUM('basic', 'verified_basic', 'verified_premium', 'official', 'developer') DEFAULT 'basic',
  `bio` VARCHAR(500) DEFAULT '',
  `birthdate` DATE,
  `birthdate_changed` BOOLEAN DEFAULT FALSE,
  `birthdate_changed_at` DATETIME,
  `last_birthday_notification` DATETIME,
  `ban_status` BOOLEAN DEFAULT FALSE,
  `ban_release_datetime` DATETIME,
  `google_id` VARCHAR(255) UNIQUE,
  `email_verified` BOOLEAN DEFAULT FALSE,
  `email_verification_token` TEXT,
  `email_verification_expires` DATETIME,
  `email_verified_at` DATETIME,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_username (`username`),
  INDEX idx_email (`email`),
  INDEX idx_ban_status (`ban_status`),
  INDEX idx_role (`role`),
  INDEX idx_created_at (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Maintenances Table
CREATE TABLE `maintenances` (
  `id` VARCHAR(24) PRIMARY KEY,
  `is_active` BOOLEAN DEFAULT FALSE NOT NULL,
  `estimated_end_time` DATETIME,
  `message` TEXT,
  `updated_by` VARCHAR(24),
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`updated_by`) REFERENCES `users`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Follows Table
CREATE TABLE `follows` (
  `id` VARCHAR(24) PRIMARY KEY,
  `follower_id` VARCHAR(24) NOT NULL,
  `following_id` VARCHAR(24) NOT NULL,
  `status` ENUM('active', 'blocked') DEFAULT 'active',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`follower_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`following_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  UNIQUE KEY unique_follow (`follower_id`, `following_id`),
  INDEX idx_follower_status (`follower_id`, `status`),
  INDEX idx_following_status (`following_id`, `status`),
  INDEX idx_created_at (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Frames Table
CREATE TABLE `frames` (
  `id` VARCHAR(24) PRIMARY KEY,
  `title` VARCHAR(100) NOT NULL,
  `desc` VARCHAR(500) DEFAULT '',
  `thumbnail` TEXT,
  `layout_type` ENUM('2x1', '3x1', '4x1') NOT NULL,
  `official_status` BOOLEAN DEFAULT FALSE,
  `visibility` ENUM('private', 'public') DEFAULT 'private',
  `approval_status` ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
  `approved_by` VARCHAR(24),
  `approved_at` DATETIME,
  `rejection_reason` VARCHAR(500),
  `user_id` VARCHAR(24) NOT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`approved_by`) REFERENCES `users`(`id`) ON DELETE SET NULL,
  INDEX idx_visibility_approval (`visibility`, `approval_status`),
  INDEX idx_approval_status (`approval_status`, `created_at`),
  INDEX idx_user_created (`user_id`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Frame Images (for array of images)
CREATE TABLE `frame_images` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `frame_id` VARCHAR(24) NOT NULL,
  `image_url` TEXT NOT NULL,
  `order_index` INT DEFAULT 0,
  FOREIGN KEY (`frame_id`) REFERENCES `frames`(`id`) ON DELETE CASCADE,
  INDEX idx_frame_id (`frame_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Frame Tags
CREATE TABLE `frame_tags` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `frame_id` VARCHAR(24) NOT NULL,
  `tag` VARCHAR(50) NOT NULL,
  FOREIGN KEY (`frame_id`) REFERENCES `frames`(`id`) ON DELETE CASCADE,
  INDEX idx_frame_id (`frame_id`),
  INDEX idx_tag (`tag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Frame Likes
CREATE TABLE `frame_likes` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `frame_id` VARCHAR(24) NOT NULL,
  `user_id` VARCHAR(24) NOT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`frame_id`) REFERENCES `frames`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  UNIQUE KEY unique_like (`frame_id`, `user_id`),
  INDEX idx_frame_id (`frame_id`),
  INDEX idx_user_id (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Frame Uses
CREATE TABLE `frame_uses` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `frame_id` VARCHAR(24) NOT NULL,
  `user_id` VARCHAR(24) NOT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`frame_id`) REFERENCES `frames`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX idx_frame_id (`frame_id`),
  INDEX idx_user_id (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tickets Table
CREATE TABLE `tickets` (
  `id` VARCHAR(24) PRIMARY KEY,
  `title` VARCHAR(200) NOT NULL,
  `description` VARCHAR(2000) NOT NULL,
  `user_id` VARCHAR(24) NOT NULL,
  `type` ENUM('suggestion', 'critics', 'other') NOT NULL,
  `status` ENUM('pending', 'in_progress', 'resolved', 'closed') DEFAULT 'pending',
  `admin_response` VARCHAR(2000),
  `admin_id` VARCHAR(24),
  `priority` ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`admin_id`) REFERENCES `users`(`id`) ON DELETE SET NULL,
  INDEX idx_user_created (`user_id`, `created_at`),
  INDEX idx_status_priority (`status`, `priority`),
  INDEX idx_created_at (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ticket Images
CREATE TABLE `ticket_images` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `ticket_id` VARCHAR(24) NOT NULL,
  `image_url` TEXT NOT NULL,
  `order_index` INT DEFAULT 0,
  FOREIGN KEY (`ticket_id`) REFERENCES `tickets`(`id`) ON DELETE CASCADE,
  INDEX idx_ticket_id (`ticket_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Reports Table
CREATE TABLE `reports` (
  `id` VARCHAR(24) PRIMARY KEY,
  `title` VARCHAR(200) NOT NULL,
  `description` VARCHAR(1000) NOT NULL,
  `frame_id` VARCHAR(24) NOT NULL,
  `user_id` VARCHAR(24) NOT NULL,
  `report_status` ENUM('pending', 'done', 'rejected') DEFAULT 'pending',
  `admin_response` VARCHAR(1000),
  `admin_id` VARCHAR(24),
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`frame_id`) REFERENCES `frames`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`admin_id`) REFERENCES `users`(`id`) ON DELETE SET NULL,
  INDEX idx_frame_id (`frame_id`),
  INDEX idx_user_id (`user_id`),
  INDEX idx_report_status (`report_status`),
  INDEX idx_created_at (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Photos Table
CREATE TABLE `photos` (
  `id` VARCHAR(24) PRIMARY KEY,
  `title` VARCHAR(100) NOT NULL,
  `desc` VARCHAR(500) DEFAULT '',
  `frame_id` VARCHAR(24) NOT NULL,
  `user_id` VARCHAR(24) NOT NULL,
  `expires_at` DATETIME,
  `live_photo` BOOLEAN DEFAULT FALSE,
  `ai_photo` BOOLEAN DEFAULT FALSE,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`frame_id`) REFERENCES `frames`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX idx_expires_at (`expires_at`),
  INDEX idx_user_created (`user_id`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Photo Images
CREATE TABLE `photo_images` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `photo_id` VARCHAR(24) NOT NULL,
  `image_url` TEXT NOT NULL,
  `order_index` INT DEFAULT 0,
  FOREIGN KEY (`photo_id`) REFERENCES `photos`(`id`) ON DELETE CASCADE,
  INDEX idx_photo_id (`photo_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Photo Videos
CREATE TABLE `photo_videos` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `photo_id` VARCHAR(24) NOT NULL,
  `video_url` TEXT NOT NULL,
  `order_index` INT DEFAULT 0,
  FOREIGN KEY (`photo_id`) REFERENCES `photos`(`id`) ON DELETE CASCADE,
  INDEX idx_photo_id (`photo_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Photo Collabs Table
CREATE TABLE `photo_collabs` (
  `id` VARCHAR(24) PRIMARY KEY,
  `title` VARCHAR(100) NOT NULL,
  `desc` VARCHAR(500) DEFAULT '',
  `frame_id` VARCHAR(24) NOT NULL,
  `layout_type` ENUM('2x1', '3x1', '4x1') NOT NULL,
  `inviter_user_id` VARCHAR(24) NOT NULL,
  `inviter_photo_id` VARCHAR(24) NOT NULL,
  `receiver_user_id` VARCHAR(24) NOT NULL,
  `receiver_photo_id` VARCHAR(24) NOT NULL,
  `status` ENUM('pending', 'accepted', 'rejected', 'completed') DEFAULT 'pending',
  `invitation_message` VARCHAR(200) DEFAULT '',
  `invitation_sent_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `invitation_responded_at` DATETIME,
  `expires_at` DATETIME NOT NULL,
  `completed_at` DATETIME,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`frame_id`) REFERENCES `frames`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`inviter_user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`inviter_photo_id`) REFERENCES `photos`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`receiver_user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`receiver_photo_id`) REFERENCES `photos`(`id`) ON DELETE CASCADE,
  INDEX idx_expires_at (`expires_at`),
  INDEX idx_inviter_created (`inviter_user_id`, `created_at`),
  INDEX idx_receiver_created (`receiver_user_id`, `created_at`),
  INDEX idx_status_created (`status`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Photo Collab Merged Images
CREATE TABLE `photo_collab_images` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `photo_collab_id` VARCHAR(24) NOT NULL,
  `image_url` TEXT NOT NULL,
  `order_index` INT DEFAULT 0,
  FOREIGN KEY (`photo_collab_id`) REFERENCES `photo_collabs`(`id`) ON DELETE CASCADE,
  INDEX idx_photo_collab_id (`photo_collab_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Photo Collab Stickers
CREATE TABLE `photo_collab_stickers` (
  `id` VARCHAR(50) PRIMARY KEY,
  `photo_collab_id` VARCHAR(24) NOT NULL,
  `type` ENUM('emoji', 'text', 'image') NOT NULL,
  `content` TEXT NOT NULL,
  `position_x` DECIMAL(10, 2) NOT NULL,
  `position_y` DECIMAL(10, 2) NOT NULL,
  `size_width` DECIMAL(10, 2) NOT NULL,
  `size_height` DECIMAL(10, 2) NOT NULL,
  `rotation` DECIMAL(10, 2) DEFAULT 0,
  `added_by` VARCHAR(24) NOT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`photo_collab_id`) REFERENCES `photo_collabs`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`added_by`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX idx_photo_collab_id (`photo_collab_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- AI Photobooth Usages Table
CREATE TABLE `aiphotobooth_usages` (
  `id` VARCHAR(24) PRIMARY KEY,
  `user_id` VARCHAR(24) NOT NULL,
  `username` VARCHAR(100) NOT NULL,
  `count` INT DEFAULT 0,
  `month` INT NOT NULL,
  `year` INT NOT NULL,
  `last_used_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  UNIQUE KEY unique_user_month_year (`user_id`, `month`, `year`),
  INDEX idx_user_id (`user_id`),
  INDEX idx_username (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Broadcasts Table
CREATE TABLE `broadcasts` (
  `id` VARCHAR(24) PRIMARY KEY,
  `title` VARCHAR(100) NOT NULL,
  `message` VARCHAR(500) NOT NULL,
  `type` ENUM('announcement', 'maintenance', 'update', 'alert', 'celebration', 'general') DEFAULT 'general',
  `priority` ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
  `target_audience` ENUM('all', 'verified', 'premium', 'basic', 'official', 'developer', 'online_users') DEFAULT 'all',
  `status` ENUM('draft', 'scheduled', 'sent', 'cancelled') DEFAULT 'draft',
  `scheduled_at` DATETIME,
  `sent_at` DATETIME,
  `expires_at` DATETIME,
  `created_by` VARCHAR(24) NOT NULL,
  `sent_by` VARCHAR(24),
  `total_recipients` INT DEFAULT 0,
  `notifications_created` INT DEFAULT 0,
  `delivery_online` INT DEFAULT 0,
  `delivery_offline` INT DEFAULT 0,
  `delivery_failed` INT DEFAULT 0,
  `send_to_new_users` BOOLEAN DEFAULT FALSE,
  `persistent` BOOLEAN DEFAULT TRUE,
  `dismissible` BOOLEAN DEFAULT TRUE,
  `action_url` TEXT,
  `icon` VARCHAR(100),
  `color` VARCHAR(50),
  `metadata_version` VARCHAR(50),
  `metadata_feature` VARCHAR(200),
  `metadata_maintenance_start` DATETIME,
  `metadata_maintenance_end` DATETIME,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`created_by`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`sent_by`) REFERENCES `users`(`id`) ON DELETE SET NULL,
  INDEX idx_created_by_status (`created_by`, `status`),
  INDEX idx_status_scheduled (`status`, `scheduled_at`),
  INDEX idx_created_at (`created_at`),
  INDEX idx_target_status (`target_audience`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Broadcast Target Roles
CREATE TABLE `broadcast_target_roles` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `broadcast_id` VARCHAR(24) NOT NULL,
  `role` ENUM('basic', 'verified_basic', 'verified_premium', 'official', 'developer') NOT NULL,
  FOREIGN KEY (`broadcast_id`) REFERENCES `broadcasts`(`id`) ON DELETE CASCADE,
  INDEX idx_broadcast_id (`broadcast_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Notifications Table
CREATE TABLE `notifications` (
  `id` VARCHAR(24) PRIMARY KEY,
  `recipient_id` VARCHAR(24) NOT NULL,
  `sender_id` VARCHAR(24) NOT NULL,
  `type` ENUM('frame_like', 'frame_use', 'frame_approved', 'frame_rejected', 'user_follow', 'frame_upload', 'system', 'birthday', 'broadcast') NOT NULL,
  `title` VARCHAR(100) NOT NULL,
  `message` VARCHAR(500) NOT NULL,
  `is_read` BOOLEAN DEFAULT FALSE,
  `read_at` DATETIME,
  `is_dismissible` BOOLEAN DEFAULT TRUE,
  `expires_at` DATETIME,
  `data_frame_id` VARCHAR(24),
  `data_frame_title` VARCHAR(100),
  `data_frame_thumbnail` TEXT,
  `data_follower_id` VARCHAR(24),
  `data_follower_name` VARCHAR(100),
  `data_follower_username` VARCHAR(100),
  `data_follower_image` TEXT,
  `data_owner_id` VARCHAR(24),
  `data_owner_name` VARCHAR(100),
  `data_owner_username` VARCHAR(100),
  `data_owner_image` TEXT,
  `data_birthday_user_id` VARCHAR(24),
  `data_birthday_user_name` VARCHAR(100),
  `data_birthday_user_username` VARCHAR(100),
  `data_birthday_user_age` INT,
  `data_broadcast_id` VARCHAR(24),
  `data_broadcast_type` VARCHAR(50),
  `data_broadcast_priority` VARCHAR(50),
  `data_action_url` TEXT,
  `data_custom_icon` VARCHAR(100),
  `data_custom_color` VARCHAR(50),
  `data_additional_info` JSON,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`recipient_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`sender_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX idx_recipient_created (`recipient_id`, `created_at`),
  INDEX idx_recipient_read (`recipient_id`, `is_read`),
  INDEX idx_recipient_type (`recipient_id`, `type`),
  INDEX idx_expires_at (`expires_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
