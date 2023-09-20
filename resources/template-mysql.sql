/******************************************

Description: Scriptures MySQL database dump
https://github.com/samuelbradshaw/python-scripture-scraper

******************************************/

SET NAMES utf8mb4;
START TRANSACTION;

/* CREATE TABLES */

CREATE TABLE IF NOT EXISTS Publication (
  id int(11) unsigned NOT NULL AUTO_INCREMENT,
  pubKey varchar(50) NOT NULL,
  langBcp47 varchar(12) NOT NULL,
  pubPosition int(11) NOT NULL,
  pubSlug varchar(50) NOT NULL,
  pubName varchar(150) NOT NULL,
  pubVersionSlug varchar(50) NOT NULL,
  pubVersionAbbrev varchar(10) DEFAULT NULL,
  pubVersionName varchar(50) DEFAULT NULL,
  pubEditionYear int(4) unsigned DEFAULT NULL,
  pubFirstEditionYear int(4) unsigned DEFAULT NULL,
  pubCopyrightStatement varchar(200) DEFAULT NULL,
  pubCopyrightOwner enum('pd', 'iri', 'other') DEFAULT NULL,
  pubCategory enum('bible','cjc') DEFAULT NULL,
  pubIsHistorical tinyint(1) unsigned NOT NULL DEFAULT 0,
  pubIsManuscript tinyint(1) unsigned NOT NULL DEFAULT 0,
  pubSource varchar(50) DEFAULT NULL,
  pubSourceUrl varchar(250) DEFAULT NULL,
  pubChurchUri varchar(50) DEFAULT NULL,
  pubCreatedDate timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY UQ_Publication_pubKey (pubKey),
  KEY IDX_Publication_pubPosition (pubPosition),
  KEY IDX_Publication_pubSlug (pubSlug),
  KEY IDX_Publication_pubVersionSlug (pubVersionSlug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE IF NOT EXISTS Chapter (
  id int(11) unsigned NOT NULL AUTO_INCREMENT,
  pubKey varchar(50) NOT NULL,
  chPosition int(11) NOT NULL,
  chSlug varchar(150) NOT NULL,
  chName varchar(150) NOT NULL,
  chAbbrev varchar(50) DEFAULT NULL,
  chNumber varchar(10) DEFAULT NULL,
  bookSlug varchar(50) DEFAULT NULL,
  chChurchUri varchar(50) DEFAULT NULL,
  PRIMARY KEY (id),
  KEY IDX_Chapter_pubKey_chSlug (pubKey, chSlug),
  KEY IDX_Chapter_pubKey_bookSlug (pubKey, bookSlug),
  KEY IDX_Chapter_chPosition (chPosition),
  CONSTRAINT FK_Chapter_pubKey FOREIGN KEY (pubKey) REFERENCES Publication (pubKey) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE IF NOT EXISTS ChapterMedia (
  id int(11) unsigned NOT NULL AUTO_INCREMENT,
  pubKey varchar(50) NOT NULL,
  chSlug varchar(150) NOT NULL,
  chmType enum('audio','video','pdf') NOT NULL,
  chmSubType enum('male','female','music-vocal','music-accompaniment','360p','720p','1080p','hls','youtube') DEFAULT NULL,
  chmUrl varchar(250) DEFAULT NULL,
  chmThumbUrl varchar(250) DEFAULT NULL,
  chmStartSeconds varchar(10) DEFAULT NULL,
  chmEndSeconds varchar(10) DEFAULT NULL,
  chmSource varchar(50) DEFAULT NULL,
  chmChurchAssetId varchar(100) DEFAULT NULL,
  PRIMARY KEY (id),
  KEY IDX_Chapter_pubKey_chSlug (pubKey, chSlug),
  KEY IDX_Chapter_chmType (chmType),
  CONSTRAINT FK_ChapterMedia_pubKey FOREIGN KEY (pubKey) REFERENCES Publication (pubKey) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE IF NOT EXISTS Paragraph (
  id int(11) unsigned NOT NULL AUTO_INCREMENT,
  pubKey varchar(50) NOT NULL,
  chSlug varchar(150) NOT NULL,
  parPosition int(11) NOT NULL,
  parType enum('book-title','book-subtitle','chapter-title','chapter-subtitle','section-title','verse','paragraph','image','study-section-title','study-paragraph','study-footnotes') NOT NULL,
  parId varchar(50) NOT NULL,
  parContent mediumtext NOT NULL,
  parContentHtml mediumtext NOT NULL,
  parNumber varchar(10) DEFAULT NULL,
  parPageNumber varchar(50) DEFAULT NULL,
  parCompareId varchar(200) NOT NULL,
  parChurchId varchar(50) DEFAULT NULL,
  PRIMARY KEY (id),
  KEY IDX_Paragraph_pubKey_chSlug (pubKey, chSlug),
  KEY IDX_Paragraph_parPosition (parPosition),
  KEY IDX_Paragraph_parCompareId (parCompareId),
  CONSTRAINT FK_Paragraph_pubKey FOREIGN KEY (pubKey) REFERENCES Publication (pubKey) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

/* INSERT DATA */

{0}

/* CREATE INDEXES */

SELECT IF(
  EXISTS(
    SELECT index_name FROM information_schema.statistics
    WHERE table_schema = (SELECT DATABASE()) AND table_name = 'Paragraph' AND index_type = 'FULLTEXT'
  ),
  'SELECT ''Fulltext index already exists'' AS statement;',
  'ALTER TABLE Paragraph ADD FULLTEXT INDEX FTS_Paragraph (parContent);'
) INTO @statement1;
PREPARE add_fulltext_index_statement FROM @statement1;
EXECUTE add_fulltext_index_statement;
DEALLOCATE PREPARE add_fulltext_index_statement;

COMMIT;
