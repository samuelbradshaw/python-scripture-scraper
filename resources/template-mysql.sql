/******************************************

Description: Scriptures MySQL database dump
https://github.com/samuelbradshaw/python-scripture-scraper

******************************************/

START TRANSACTION;

/* CREATE TABLES */

CREATE TABLE IF NOT EXISTS Language (
  langBcp47 varchar(12) NOT NULL,
  langChurchCode varchar(12) NOT NULL,
  langAutonym varchar(50) NOT NULL,
  PRIMARY KEY (langBcp47)
);

CREATE TABLE IF NOT EXISTS Volume (
  volumeSlug varchar(50) NOT NULL,
  langBcp47 varchar(12) NOT NULL,
  volumeName varchar(50) NOT NULL,
  volumeAbbrev varchar(50) DEFAULT NULL,
  volumePosition int(11) NOT NULL,
  volumeChurchUri varchar(50) NOT NULL,
  PRIMARY KEY (volumeSlug, langBcp47),
  KEY IDX_Volume_volumePosition (volumePosition),
  CONSTRAINT FK_Volume_langBcp47 FOREIGN KEY (langBcp47) REFERENCES Language (langBcp47) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Book (
  bookSlug varchar(50) NOT NULL,
  langBcp47 varchar(12) NOT NULL,
  bookName varchar(50) NOT NULL,
  bookAbbrev varchar(50) DEFAULT NULL,
  bookPosition int(11) NOT NULL,
  bookChurchUri varchar(50) NOT NULL,
  volumeSlug varchar(50) NOT NULL,
  PRIMARY KEY (bookSlug, langBcp47),
  KEY IDX_Book_bookPosition (bookPosition),
  CONSTRAINT FK_Book_volumeSlug_langBcp47 FOREIGN KEY (volumeSlug, langBcp47) REFERENCES Volume (volumeSlug, langBcp47) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Chapter (
  chapterSlug varchar(50) NOT NULL,
  langBcp47 varchar(12) NOT NULL,
  chapterName varchar(50) NOT NULL,
  chapterAbbrev varchar(50) DEFAULT NULL,
  chapterNumber varchar(10) NOT NULL,
  chapterPosition int(11) NOT NULL,
  chapterChurchUri varchar(50) NOT NULL,
  bookSlug varchar(50) NOT NULL,
  PRIMARY KEY (chapterSlug, langBcp47),
  KEY IDX_Chapter_chapterPosition (chapterPosition),
  CONSTRAINT FK_Chapter_bookSlug_langBcp47 FOREIGN KEY (bookSlug, langBcp47) REFERENCES Book (bookSlug, langBcp47) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Paragraph (
  paraSlug varchar(50) NOT NULL,
  langBcp47 varchar(12) NOT NULL,
  paraType enum('book-title','chapter-title','section-title','subtitle','verse','paragraph','image') NOT NULL,
  paraNumber varchar(10) DEFAULT NULL,
  paraContent text NOT NULL,
  paraPosition int(11) NOT NULL,
  paraChurchId varchar(50) NOT NULL,
  chapterSlug varchar(50) NOT NULL,
  PRIMARY KEY (paraSlug, langBcp47),
  KEY IDX_Paragraph_paraPosition (paraPosition),
  CONSTRAINT FK_Paragraph_chapterSlug_langBcp47 FOREIGN KEY (chapterSlug, langBcp47) REFERENCES Chapter (chapterSlug, langBcp47) ON DELETE RESTRICT ON UPDATE CASCADE
);

/* INSERT DATA */

{0}

/* CREATE INDEXES */

SELECT IF(
  EXISTS(
    SELECT index_name FROM information_schema.statistics
    WHERE table_schema = (SELECT DATABASE()) AND table_name = 'Paragraph' AND index_type = 'FULLTEXT'
  ),
  'SELECT ''Index already exists'' AS statement;',
  'ALTER TABLE Paragraph ADD FULLTEXT(paraContent);'
) INTO @a;
PREPARE add_fulltext_index_statement FROM @a;
EXECUTE add_fulltext_index_statement;
DEALLOCATE PREPARE add_fulltext_index_statement;

COMMIT;
