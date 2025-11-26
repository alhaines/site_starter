-- phpMyAdmin SQL Dump
-- version 5.2.2deb1
-- https://www.phpmyadmin.net/
--
-- Sample database structure for site_starter
-- Generation Time: Nov 26, 2025
-- Server version: 11.8.3-MariaDB
-- PHP Version: 8.4.11

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `your_database`
--

-- --------------------------------------------------------

--
-- Table structure for table `siteslinks`
--
DROP TABLE IF EXISTS `siteslinks`;

CREATE TABLE `siteslinks` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `link` varchar(255) DEFAULT NULL,
  `level` varchar(2) DEFAULT NULL,
  `comment` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `siteslinks`
-- These are SAMPLE entries. Customize them for your site.
--

INSERT INTO `siteslinks` (`id`, `title`, `link`, `level`, `comment`) VALUES
(1, 'My Media Library', 'http://media.your_domain', '1', 'Media Library'),
(2, 'Photo Gallery', '/gallery/photos/', '1', 'Photo Gallery'),
(3, 'My Book Library', 'http://books.your_domain', '1', 'Book Library'),
(4, 'Address Book', 'http://address.your_domain', '2', 'Address Book'),
(5, 'Shopping List', '/shopping', '1', 'Shopping list'),
(6, 'My Blog', 'https://blog.your_domain/', '2', 'Personal Blog'),
(7, 'File Browser', 'http://files.your_domain', '3', 'File Browser (Admin Only)'),
(8, 'Admin Panel', 'https://admin.your_domain/', '3', 'Admin Panel (Admin Only)');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `siteslinks`
--
ALTER TABLE `siteslinks`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `siteslinks`
--
ALTER TABLE `siteslinks`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
