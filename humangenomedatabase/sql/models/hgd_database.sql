CREATE DATABASE  IF NOT EXISTS `human_genome_database` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `human_genome_database`;
-- MySQL dump 10.13  Distrib 8.0.34, for macos13 (arm64)
--
-- Host: localhost    Database: human_genome_database
-- ------------------------------------------------------
-- Server version	8.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `kegg_human_disease`
--

DROP TABLE IF EXISTS `kegg_human_disease`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kegg_human_disease` (
  `DISEASE_ID` varchar(10) NOT NULL,
  `DISEASE_NAME_COUNT` int NOT NULL,
  PRIMARY KEY (`DISEASE_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `kegg_human_disease_name_lookup`
--

DROP TABLE IF EXISTS `kegg_human_disease_name_lookup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kegg_human_disease_name_lookup` (
  `DISEASE_ID` varchar(10) NOT NULL,
  `DISEASE_NAME` text NOT NULL,
  `LOOKUP_SOURCE` char(7) NOT NULL,
  KEY `DISEASE_ID_idx` (`DISEASE_ID`),
  CONSTRAINT `DISEASE_ID` FOREIGN KEY (`DISEASE_ID`) REFERENCES `kegg_human_disease` (`DISEASE_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `kegg_human_gene`
--

DROP TABLE IF EXISTS `kegg_human_gene`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kegg_human_gene` (
  `GENE_ID` varchar(10) NOT NULL,
  `GENE_TYPE` varchar(5) NOT NULL,
  `GENE_NAME` text NOT NULL,
  `CHRSTOP` int DEFAULT NULL,
  `CHRSTART` int DEFAULT NULL,
  `CHR_COMPLEMENT` int DEFAULT NULL,
  `CHROMOSOME` varchar(8) DEFAULT NULL,
  PRIMARY KEY (`GENE_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `kegg_human_gene_disease_lookup`
--

DROP TABLE IF EXISTS `kegg_human_gene_disease_lookup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kegg_human_gene_disease_lookup` (
  `GENE_ID` varchar(10) NOT NULL,
  `DISEASE_ID` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `kegg_human_gene_symbol_lookup`
--

DROP TABLE IF EXISTS `kegg_human_gene_symbol_lookup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kegg_human_gene_symbol_lookup` (
  `GENE_ID` varchar(10) NOT NULL,
  `GENE_SYMBOL` varchar(35) NOT NULL,
  `GENE_ALIAS_NO` int NOT NULL,
  `lookup_source` char(4) NOT NULL,
  KEY `GENE_ID_idx` (`GENE_ID`),
  CONSTRAINT `GENE_ID` FOREIGN KEY (`GENE_ID`) REFERENCES `kegg_human_gene` (`GENE_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `kegg_human_module`
--

DROP TABLE IF EXISTS `kegg_human_module`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kegg_human_module` (
  `MODULE_ID` varchar(10) NOT NULL,
  `MODULE_NAME_COUNT` int NOT NULL,
  PRIMARY KEY (`MODULE_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `kegg_human_module_name_lookup`
--

DROP TABLE IF EXISTS `kegg_human_module_name_lookup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kegg_human_module_name_lookup` (
  `MODULE_ID` varchar(10) NOT NULL,
  `MODULE_NAME` varchar(100) NOT NULL,
  `LOOKUP_SOURCE` char(6) NOT NULL,
  KEY `MODULE_ID_idx` (`MODULE_ID`),
  CONSTRAINT `MODULE_ID` FOREIGN KEY (`MODULE_ID`) REFERENCES `kegg_human_module` (`MODULE_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `kegg_human_pathway`
--

DROP TABLE IF EXISTS `kegg_human_pathway`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kegg_human_pathway` (
  `PATHWAY_ID` varchar(10) NOT NULL,
  `PATHWAY_NAME` varchar(100) NOT NULL,
  PRIMARY KEY (`PATHWAY_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `kegg_human_pathway_disease_lookup`
--

DROP TABLE IF EXISTS `kegg_human_pathway_disease_lookup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kegg_human_pathway_disease_lookup` (
  `PATHWAY_ID` varchar(10) NOT NULL,
  `DISEASE_ID` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `kegg_human_pathway_gene_lookup`
--

DROP TABLE IF EXISTS `kegg_human_pathway_gene_lookup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kegg_human_pathway_gene_lookup` (
  `PATHWAY_ID` varchar(10) NOT NULL,
  `GENE_ID` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `kegg_human_pathway_module_lookup`
--

DROP TABLE IF EXISTS `kegg_human_pathway_module_lookup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kegg_human_pathway_module_lookup` (
  `PATHWAY_ID` varchar(10) NOT NULL,
  `MODULE_ID` varchar(10) NOT NULL,
  KEY `PATHWAY_ID_idx` (`PATHWAY_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `kegg_human_variant`
--

DROP TABLE IF EXISTS `kegg_human_variant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kegg_human_variant` (
  `VARIANT_ID` varchar(10) NOT NULL,
  `VARIANT_NAME` varchar(100) NOT NULL,
  `VARIANT_VERSION` int NOT NULL,
  `GENE_SYMBOL` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ncbi_human_gene2go`
--

DROP TABLE IF EXISTS `ncbi_human_gene2go`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ncbi_human_gene2go` (
  `GENE_ID` varchar(10) NOT NULL,
  `GO_ID` varchar(10) NOT NULL,
  `EVIDENCE` varchar(4) NOT NULL,
  `QUALIFIER` varchar(50) NOT NULL,
  `GO_TERM` text NOT NULL,
  `CATEGORY` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ncbi_human_gene_info`
--

DROP TABLE IF EXISTS `ncbi_human_gene_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ncbi_human_gene_info` (
  `GENE_ID` varchar(10) NOT NULL,
  `CHROMOSOME` varchar(10) NOT NULL,
  `MAP_LOCATION` varchar(50) NOT NULL,
  `DESCRIPTION` text NOT NULL,
  `GENE_TYPE` varchar(20) NOT NULL,
  `GENE_SYMBOL` varchar(35) NOT NULL,
  `GENE_NAME` text,
  `NOMENCLATURE_STATUS` tinyint(1) NOT NULL,
  PRIMARY KEY (`GENE_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ncbi_human_gene_info_dbxref_lookup`
--

DROP TABLE IF EXISTS `ncbi_human_gene_info_dbxref_lookup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ncbi_human_gene_info_dbxref_lookup` (
  `GENE_ID` varchar(10) NOT NULL,
  `REF_ID` varchar(20) NOT NULL,
  `REF` varchar(20) NOT NULL,
  `LOOKUP_SOURCE` char(9) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ncbi_human_gene_info_feature_lookup`
--

DROP TABLE IF EXISTS `ncbi_human_gene_info_feature_lookup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ncbi_human_gene_info_feature_lookup` (
  `GENE_ID` varchar(10) NOT NULL,
  `FEATURE_CAT` varchar(20) NOT NULL,
  `FEATURE` varchar(50) NOT NULL,
  `LOOKUP_SOURCE` char(9) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ncbi_human_gene_info_otherdesig_lookup`
--

DROP TABLE IF EXISTS `ncbi_human_gene_info_otherdesig_lookup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ncbi_human_gene_info_otherdesig_lookup` (
  `GENE_ID` varchar(10) NOT NULL,
  `OTHER_DESIGNATIONS` text NOT NULL,
  `LOOKUP_SOURCE` char(9) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ncbi_human_gene_info_symbol_lookup`
--

DROP TABLE IF EXISTS `ncbi_human_gene_info_symbol_lookup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ncbi_human_gene_info_symbol_lookup` (
  `GENE_ID` varchar(10) NOT NULL,
  `GENE_SYMBOL` varchar(35) NOT NULL,
  `LOOKUP_SOURCE` char(9) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ncbi_human_gene_ortholog`
--

DROP TABLE IF EXISTS `ncbi_human_gene_ortholog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ncbi_human_gene_ortholog` (
  `GENE_ID` varchar(10) NOT NULL,
  `OTHER_TAX_ID` int NOT NULL,
  `OTHER_GENE_ID` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ncbi_human_gene_summary`
--

DROP TABLE IF EXISTS `ncbi_human_gene_summary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ncbi_human_gene_summary` (
  `GENE_ID` varchar(10) NOT NULL,
  `GENE_SYMBOL` varchar(35) NOT NULL,
  `DESCRIPTION` text NOT NULL,
  `CHROMOSOME` varchar(10) NOT NULL,
  `MAP_LOCATION` varchar(50) DEFAULT NULL,
  `GENE_NAME` text,
  `GENE_WEIGHT` int NOT NULL,
  `SUMMARY` text,
  `CHRSTART` int NOT NULL,
  `CHRSTOP` int NOT NULL,
  `EXONCOUNT` float DEFAULT NULL,
  PRIMARY KEY (`GENE_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ncbi_human_gene_summary_omim_lookup`
--

DROP TABLE IF EXISTS `ncbi_human_gene_summary_omim_lookup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ncbi_human_gene_summary_omim_lookup` (
  `GENE_ID` varchar(10) NOT NULL,
  `MIM_ID` int NOT NULL,
  `LOOKUP_SOURCE` char(12) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ncbi_human_gene_summary_symbol_lookup`
--

DROP TABLE IF EXISTS `ncbi_human_gene_summary_symbol_lookup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ncbi_human_gene_summary_symbol_lookup` (
  `GENE_ID` varchar(10) NOT NULL,
  `GENE_SYMBOL` varchar(35) NOT NULL,
  `LOOKUP_SOURCE` char(12) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ncbi_human_snp_summary`
--

DROP TABLE IF EXISTS `ncbi_human_snp_summary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ncbi_human_snp_summary` (
  `SNP_ID` varchar(15) NOT NULL,
  `MAP_LOCATION` varchar(25) NOT NULL,
  `SEQ` text NOT NULL,
  `CLINICAL_SIGNIFICANCE` text,
  `CHROMOSOME` varchar(15) NOT NULL,
  `SPDI` text NOT NULL,
  `VALIDATED` varchar(35) NOT NULL,
  `UPD_BUILD` int NOT NULL,
  `ALLELE` char(1) NOT NULL,
  `SNP_CLASS` varchar(7) NOT NULL,
  `LEN` int NOT NULL,
  `HGVS` text NOT NULL,
  PRIMARY KEY (`SNP_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ncbi_human_snp_summary_fxn_lookup`
--

DROP TABLE IF EXISTS `ncbi_human_snp_summary_fxn_lookup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ncbi_human_snp_summary_fxn_lookup` (
  `SNP_ID` varchar(15) NOT NULL,
  `FXN_CLASS` varchar(35) NOT NULL,
  `LOOKUP_SOURCE` char(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ncbi_human_snp_summary_gene_lookup`
--

DROP TABLE IF EXISTS `ncbi_human_snp_summary_gene_lookup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ncbi_human_snp_summary_gene_lookup` (
  `SNP_ID` varchar(15) NOT NULL,
  `GENE_ID` varchar(10) NOT NULL,
  `LOOKUP_SOURCE` char(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ncbi_human_snp_summary_ss_lookup`
--

DROP TABLE IF EXISTS `ncbi_human_snp_summary_ss_lookup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ncbi_human_snp_summary_ss_lookup` (
  `SNP_ID` varchar(15) NOT NULL,
  `SS` varchar(10) NOT NULL,
  `LOOKUP_SOURCE` char(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-12-27 18:16:23
