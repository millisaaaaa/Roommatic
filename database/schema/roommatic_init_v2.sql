-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1
-- 產生時間： 2026-04-09 16:50:07
-- 伺服器版本： 10.4.32-MariaDB
-- PHP 版本： 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 資料庫： `roommatic`
--

-- --------------------------------------------------------

--
-- 資料表結構 `org`
--

CREATE TABLE `org` (
  `org_id` int(11) NOT NULL,
  `org_name` varchar(150) DEFAULT NULL,
  `org_admid` int(11) NOT NULL,
  `org_password` varchar(255) DEFAULT NULL,
  `plan_id` int(11) DEFAULT NULL,
  `start_date` datetime DEFAULT NULL,
  `end_date` datetime DEFAULT NULL,
  `space` int(11) DEFAULT NULL,
  `org_status` enum('active','expire','canceled') DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- 傾印資料表的資料 `org`
--

INSERT INTO `org` (`org_id`, `org_name`, `org_admid`, `org_password`, `plan_id`, `start_date`, `end_date`, `space`, `org_status`) VALUES
(1, 'Roommatic Team', 1, 'org123', 2, '2026-04-09 22:47:07', '2026-05-09 22:47:07', 10, 'active');

-- --------------------------------------------------------

--
-- 資料表結構 `plans`
--

CREATE TABLE `plans` (
  `plan_id` int(11) NOT NULL,
  `plan_name` varchar(50) NOT NULL,
  `max_space` int(11) NOT NULL,
  `price` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- 傾印資料表的資料 `plans`
--

INSERT INTO `plans` (`plan_id`, `plan_name`, `max_space`, `price`) VALUES
(1, 'solo', 3, 0),
(2, 'multi', 10, 0),
(3, 'enterprise', 30, 0);

-- --------------------------------------------------------

--
-- 資料表結構 `rooms`
--

CREATE TABLE `rooms` (
  `room_id` int(11) NOT NULL,
  `org_id` int(11) NOT NULL,
  `room_name` varchar(50) NOT NULL,
  `type` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- 傾印資料表的資料 `rooms`
--

INSERT INTO `rooms` (`room_id`, `org_id`, `room_name`, `type`) VALUES
(1, 1, 'R101', 'discussion'),
(2, 1, 'R102', 'meeting');

-- --------------------------------------------------------
sql
-- 新增設備相關資料表
-- 適用於已建立 v1 資料庫後，補上設備型錄、房間設備與紅外線控制碼資料表

USE roommatic;

-- --------------------------------------------------------
-- appliance_catalog：設備型錄表
-- --------------------------------------------------------

CREATE TABLE IF NOT EXISTS appliance_catalog (
    appliance_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    category ENUM('air_conditioner', 'fan', 'light') NOT NULL,
    brand VARCHAR(100),
    model VARCHAR(150),
    rated_power FLOAT,
    source_type ENUM('crawler', 'manual', 'preset') NOT NULL DEFAULT 'manual',
    source_url VARCHAR(500),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_appliance_identity (category, brand, model)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- room_appliances：房間設備表
-- --------------------------------------------------------

CREATE TABLE IF NOT EXISTS room_appliances (
    room_appliance_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    room_id INT NOT NULL,
    appliance_id INT,
    appliance_name VARCHAR(150) NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    custom_power FLOAT,
    control_method ENUM('IR', 'manual', 'none') DEFAULT 'none',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_room_appliances_room
        FOREIGN KEY (room_id) REFERENCES rooms(room_id),
    CONSTRAINT fk_room_appliances_catalog
        FOREIGN KEY (appliance_id) REFERENCES appliance_catalog(appliance_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- device_ir_codes：設備紅外線控制碼表
-- --------------------------------------------------------

CREATE TABLE IF NOT EXISTS device_ir_codes (
    ir_code_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    room_appliance_id INT NOT NULL,
    function_key VARCHAR(100) NOT NULL,
    raw_code TEXT NOT NULL,
    is_verified TINYINT(1) NOT NULL DEFAULT 0,
    learned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ir_codes_room_appliance
        FOREIGN KEY (room_appliance_id) REFERENCES room_appliances(room_appliance_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


--
-- 資料表結構 `updates`
--

CREATE TABLE `updates` (
  `update_id` int(11) NOT NULL,
  `room_id` int(11) DEFAULT NULL,
  `update_time` datetime NOT NULL,
  `ta` float DEFAULT NULL,
  `Rh` float DEFAULT NULL,
  `people_num` int(11) DEFAULT NULL,
  `PMV` float DEFAULT NULL,
  `PPD` float DEFAULT NULL,
  `light_status` enum('on','off') DEFAULT NULL,
  `con_status` enum('on','off') DEFAULT NULL,
  `con_temp` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- 傾印資料表的資料 `updates`
--

INSERT INTO `updates` (`update_id`, `room_id`, `update_time`, `ta`, `Rh`, `people_num`, `PMV`, `PPD`, `light_status`, `con_status`, `con_temp`) VALUES
(1, 1, '2026-04-09 22:47:07', 25.6, 58, 4, 0.3, 8, 'on', 'on', 24),
(2, 2, '2026-04-09 22:47:07', 27.1, 62, 0, 0.8, 18, 'off', 'off', 28);

-- --------------------------------------------------------

--
-- 資料表結構 `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `username` varchar(150) NOT NULL,
  `email` varchar(255) NOT NULL,
  `user_password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- 傾印資料表的資料 `users`
--

INSERT INTO `users` (`user_id`, `username`, `email`, `user_password`) VALUES
(1, 'admin1', 'admin1@test.com', '123456'),
(2, 'member1', 'member1@test.com', '123456');

-- --------------------------------------------------------

--
-- 資料表結構 `user_org`
--

CREATE TABLE `user_org` (
  `user_id` int(11) NOT NULL,
  `org_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- 傾印資料表的資料 `user_org`
--

INSERT INTO `user_org` (`user_id`, `org_id`) VALUES
(1, 1),
(2, 1);

--
-- 已傾印資料表的索引
--

--
-- 資料表索引 `org`
--
ALTER TABLE `org`
  ADD PRIMARY KEY (`org_id`),
  ADD KEY `fk_org_plan` (`plan_id`),
  ADD KEY `fk_org_admin` (`org_admid`);

--
-- 資料表索引 `plans`
--
ALTER TABLE `plans`
  ADD PRIMARY KEY (`plan_id`);

--
-- 資料表索引 `rooms`
--
ALTER TABLE `rooms`
  ADD PRIMARY KEY (`room_id`),
  ADD KEY `fk_rooms_org` (`org_id`);

--
-- 資料表索引 `updates`
--
ALTER TABLE `updates`
  ADD PRIMARY KEY (`update_id`),
  ADD KEY `fk_update_room` (`room_id`);

--
-- 資料表索引 `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- 資料表索引 `user_org`
--
ALTER TABLE `user_org`
  ADD PRIMARY KEY (`user_id`,`org_id`),
  ADD KEY `fk_user_org_org` (`org_id`);

--
-- 在傾印的資料表使用自動遞增(AUTO_INCREMENT)
--

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `org`
--
ALTER TABLE `org`
  MODIFY `org_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `plans`
--
ALTER TABLE `plans`
  MODIFY `plan_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `rooms`
--
ALTER TABLE `rooms`
  MODIFY `room_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `updates`
--
ALTER TABLE `updates`
  MODIFY `update_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- 已傾印資料表的限制式
--

--
-- 資料表的限制式 `org`
--
ALTER TABLE `org`
  ADD CONSTRAINT `fk_org_admin` FOREIGN KEY (`org_admid`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `fk_org_plan` FOREIGN KEY (`plan_id`) REFERENCES `plans` (`plan_id`);

--
-- 資料表的限制式 `rooms`
--
ALTER TABLE `rooms`
  ADD CONSTRAINT `fk_rooms_org` FOREIGN KEY (`org_id`) REFERENCES `org` (`org_id`);

--
-- 資料表的限制式 `updates`
--
ALTER TABLE `updates`
  ADD CONSTRAINT `fk_update_room` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`room_id`);

--
-- 資料表的限制式 `user_org`
--
ALTER TABLE `user_org`
  ADD CONSTRAINT `fk_user_org_org` FOREIGN KEY (`org_id`) REFERENCES `org` (`org_id`),
  ADD CONSTRAINT `fk_user_org_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
