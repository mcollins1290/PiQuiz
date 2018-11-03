-- MySQL dump 10.16  Distrib 10.1.23-MariaDB, for debian-linux-gnueabihf (armv7l)
--
-- Host: localhost    Database: piquiz
-- ------------------------------------------------------
-- Server version	10.1.23-MariaDB-9+deb9u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Temporary table structure for view `INVALID_QUESTIONS`
--

DROP TABLE IF EXISTS `INVALID_QUESTIONS`;
/*!50001 DROP VIEW IF EXISTS `INVALID_QUESTIONS`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `INVALID_QUESTIONS` (
  `question_id` tinyint NOT NULL,
  `question_text` tinyint NOT NULL,
  `answer_id` tinyint NOT NULL,
  `archived` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `answers`
--

DROP TABLE IF EXISTS `answers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `answers` (
  `answer_id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Primary Key',
  `question_id` int(10) unsigned COMMENT 'The Question (ID) which an answer relates to',
  `answer_text` text COMMENT 'The Answer',
  PRIMARY KEY (`answer_id`),
  KEY `FK1_QUESTION_ID` (`question_id`),
  CONSTRAINT `FK1_QUESTION_ID` FOREIGN KEY (`question_id`) REFERENCES `questions` (`question_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COMMENT='A collection of Answers to the Questions posed in the ''questions'' table.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `answers`
--

LOCK TABLES `answers` WRITE;
/*!40000 ALTER TABLE `answers` DISABLE KEYS */;
INSERT INTO `answers` VALUES (1,1,'Scotland'),(2,1,'Winchester'),(3,1,'Liverpool'),(4,1,'London'),(5,2,'True'),(6,2,'False'),(7,3,'1839'),(8,3,'1843'),(9,3,'1833'),(10,3,'1848');
/*!40000 ALTER TABLE `answers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `questions`
--

DROP TABLE IF EXISTS `questions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `questions` (
  `question_id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Primary Key',
  `question_text` text COMMENT 'The Question',
  `answer_id` int(10) unsigned DEFAULT NULL COMMENT 'The Answer (ID from the Answer table)',
  `archived` tinyint(1) unsigned DEFAULT '0' COMMENT 'Archived?',
  PRIMARY KEY (`question_id`),
  KEY `FK1_ANSWER_ID` (`answer_id`),
  CONSTRAINT `FK1_ANSWER_ID` FOREIGN KEY (`answer_id`) REFERENCES `answers` (`answer_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COMMENT='A collection of Questions that PiQuiz will ask a Player.\r\nAny Questions which has Archived = 1 (True) set will be ignored.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questions`
--

LOCK TABLES `questions` WRITE;
/*!40000 ALTER TABLE `questions` DISABLE KEYS */;
INSERT INTO `questions` VALUES (1,'What town is the capital of the United Kingdom?',4,0),(2,'Is Earth closest to the Sun in January?',5,0),(3,'First Afghan War took place in which year?',7,0);
/*!40000 ALTER TABLE `questions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Final view structure for view `INVALID_QUESTIONS`
--

/*!50001 DROP TABLE IF EXISTS `INVALID_QUESTIONS`*/;
/*!50001 DROP VIEW IF EXISTS `INVALID_QUESTIONS`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `INVALID_QUESTIONS` AS select `q`.`question_id` AS `question_id`,`q`.`question_text` AS `question_text`,`q`.`answer_id` AS `answer_id`,`q`.`archived` AS `archived` from `questions` `q` where (isnull(`q`.`answer_id`) and (`q`.`archived` = 0)) order by `q`.`question_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-11-02 21:15:38
