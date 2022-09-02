/******************************************

Description: Scriptures SQLite database dump
https://github.com/samuelbradshaw/python-scripture-scraper

******************************************/

PRAGMA foreign_keys = ON;

/* CREATE TABLES */

CREATE TABLE IF NOT EXISTS Language (
  langBcp47 TEXT NOT NULL,
  langChurchCode TEXT NOT NULL,
  langAutonym TEXT NOT NULL,
  PRIMARY KEY (langBcp47)
);

CREATE TABLE IF NOT EXISTS Volume (
  volumeSlug TEXT NOT NULL,
  langBcp47 TEXT NOT NULL,
  volumeName TEXT NOT NULL,
  volumeAbbrev TEXT,
  volumePosition INTEGER NOT NULL,
  volumeChurchUri TEXT NOT NULL,
  PRIMARY KEY (volumeSlug, langBcp47),
  FOREIGN KEY (langBcp47) REFERENCES Language (langBcp47) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Book (
  bookSlug TEXT NOT NULL,
  langBcp47 TEXT NOT NULL,
  bookName TEXT NOT NULL,
  bookAbbrev TEXT,
  bookPosition INTEGER NOT NULL,
  bookChurchUri TEXT NOT NULL,
  volumeSlug TEXT NOT NULL,
  PRIMARY KEY (bookSlug, langBcp47),
  FOREIGN KEY (volumeSlug, langBcp47) REFERENCES Volume (volumeSlug, langBcp47) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Chapter (
  chapterSlug TEXT NOT NULL,
  langBcp47 TEXT NOT NULL,
  chapterName TEXT NOT NULL,
  chapterAbbrev TEXT,
  chapterNumber TEXT NOT NULL,
  chapterPosition INTEGER NOT NULL,
  chapterChurchUri TEXT NOT NULL,
  bookSlug TEXT NOT NULL,
  PRIMARY KEY (chapterSlug, langBcp47),
  FOREIGN KEY (bookSlug, langBcp47) REFERENCES Book (bookSlug, langBcp47) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Paragraph (
  paraSlug TEXT NOT NULL,
  langBcp47 TEXT NOT NULL,
  paraType TEXT NOT NULL,
  paraNumber TEXT,
  paraContent TEXT NOT NULL,
  paraPosition INTEGER NOT NULL,
  paraChurchId TEXT NOT NULL,
  chapterSlug TEXT NOT NULL,
  PRIMARY KEY (paraSlug, langBcp47),
  FOREIGN KEY (chapterSlug, langBcp47) REFERENCES Chapter (chapterSlug, langBcp47) ON DELETE RESTRICT ON UPDATE CASCADE
);


/* INSERT DATA */

{0}

/* CREATE INDEXES */

DROP INDEX IF EXISTS IDX_Volume_langBcp47;
DROP INDEX IF EXISTS IDX_Volume_volumePosition;
DROP INDEX IF EXISTS IDX_Book_volumeSlug_langBcp47;
DROP INDEX IF EXISTS IDX_Book_bookPosition;
DROP INDEX IF EXISTS IDX_Chapter_bookSlug_langBcp47;
DROP INDEX IF EXISTS IDX_Chapter_chapterPosition;
DROP INDEX IF EXISTS IDX_Paragraph_chapterSlug_langBcp47;
DROP INDEX IF EXISTS IDX_Paragraph_paraPosition;
CREATE INDEX IDX_Volume_langBcp47 ON Volume (langBcp47);
CREATE INDEX IDX_Volume_volumePosition ON Volume (volumePosition);
CREATE INDEX IDX_Book_volumeSlug_langBcp47 ON Book (volumeSlug, langBcp47);
CREATE INDEX IDX_Book_bookPosition ON Book (bookPosition);
CREATE INDEX IDX_Chapter_bookSlug_langBcp47 ON Chapter (bookSlug, langBcp47);
CREATE INDEX IDX_Chapter_chapterPosition ON Chapter (chapterPosition);
CREATE INDEX IDX_Paragraph_chapterSlug_langBcp47 ON Paragraph (chapterSlug, langBcp47);
CREATE INDEX IDX_Paragraph_paraPosition ON Paragraph (paraPosition);

DROP TABLE IF EXISTS ParagraphFts;
CREATE VIRTUAL TABLE ParagraphFts USING fts4 (
  paraContent,
  tokenize=porter
);
INSERT INTO ParagraphFts (docid, paraContent) SELECT rowid, paraContent FROM Paragraph;

VACUUM;
