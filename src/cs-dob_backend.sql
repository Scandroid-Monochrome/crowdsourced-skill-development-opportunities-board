-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Jun 15, 2026 at 01:45 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `cs-dob_backend`
--

-- --------------------------------------------------------

--
-- Table structure for table `opportunities`
--

CREATE TABLE `opportunities` (
  `ID` int(11) NOT NULL,
  `name` varchar(40) NOT NULL,
  `description` text NOT NULL,
  `link` varchar(100) NOT NULL,
  `repeatable` tinyint(1) NOT NULL,
  `user` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `opportunities`
--

INSERT INTO `opportunities` (`ID`, `name`, `description`, `link`, `repeatable`, `user`) VALUES
(1, 'Sundai Hackathon 127', 'Hackathon focusing \"on building full-stack application architectures: users, authentication, databases, APIs, observability, security, and everything needed to move beyond localhost and ship real software.\"\r\n\r\nLots of fun!', 'https://partiful.com/e/OBlUPwkSfQ46zwYlU81p', 1, 'N/A');

-- --------------------------------------------------------

--
-- Table structure for table `opp_location`
--

CREATE TABLE `opp_location` (
  `opp_ID` int(11) NOT NULL,
  `lat` decimal(10,7) NOT NULL,
  `lon` decimal(10,7) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `opp_professions`
--

CREATE TABLE `opp_professions` (
  `opp_ID` int(11) NOT NULL,
  `profession` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `opp_professions`
--

INSERT INTO `opp_professions` (`opp_ID`, `profession`) VALUES
(1, 'Software Engineering'),
(1, 'Artificial Intelligence');

-- --------------------------------------------------------

--
-- Table structure for table `professions`
--

CREATE TABLE `professions` (
  `Profession_Name` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `professions`
--

INSERT INTO `professions` (`Profession_Name`) VALUES
('Artificial Intelligence'),
('Biotech'),
('Chemical Engineering'),
('Mechanical Engineering'),
('Robotics'),
('Software Engineering');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `opportunities`
--
ALTER TABLE `opportunities`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `opp_location`
--
ALTER TABLE `opp_location`
  ADD KEY `foreign_key_opp` (`opp_ID`);

--
-- Indexes for table `opp_professions`
--
ALTER TABLE `opp_professions`
  ADD KEY `foreign_key_opp` (`opp_ID`),
  ADD KEY `foreign_key_prof` (`profession`);

--
-- Indexes for table `professions`
--
ALTER TABLE `professions`
  ADD PRIMARY KEY (`Profession_Name`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `opportunities`
--
ALTER TABLE `opportunities`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `opp_location`
--
ALTER TABLE `opp_location`
  ADD CONSTRAINT `opp_location_ibfk_1` FOREIGN KEY (`opp_ID`) REFERENCES `opportunities` (`ID`) ON DELETE CASCADE;

--
-- Constraints for table `opp_professions`
--
ALTER TABLE `opp_professions`
  ADD CONSTRAINT `opp_professions_ibfk_1` FOREIGN KEY (`opp_ID`) REFERENCES `opportunities` (`ID`) ON DELETE CASCADE,
  ADD CONSTRAINT `opp_professions_ibfk_2` FOREIGN KEY (`profession`) REFERENCES `professions` (`Profession_Name`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
