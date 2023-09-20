/******************************************

Description: Scriptures SQLite database dump
https://github.com/samuelbradshaw/python-scripture-scraper

******************************************/

PRAGMA foreign_keys = ON;

/* CREATE TABLES */

CREATE TABLE IF NOT EXISTS Publication (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pubKey TEXT NOT NULL,
  langBcp47 TEXT NOT NULL,
  pubPosition INTEGER NOT NULL,
  pubSlug TEXT NOT NULL,
  pubName TEXT NOT NULL,
  pubVersionSlug TEXT NOT NULL,
  pubVersionAbbrev TEXT,
  pubVersionName TEXT,
  pubEditionYear INTEGER,
  pubFirstEditionYear INTEGER,
  pubCopyrightStatement TEXT,
  pubCopyrightOwner TEXT,
  pubCategory TEXT,
  pubIsHistorical INTEGER NOT NULL DEFAULT 0,
  pubIsManuscript INTEGER NOT NULL DEFAULT 0,
  pubSource TEXT,
  pubSourceUrl TEXT,
  pubChurchUri TEXT,
  pubCreatedDate DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(pubKey)
);

CREATE TABLE IF NOT EXISTS Chapter (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pubKey TEXT NOT NULL,
  chPosition INTEGER NOT NULL,
  chSlug TEXT NOT NULL,
  chName TEXT NOT NULL,
  chAbbrev TEXT,
  chNumber TEXT,
  bookSlug TEXT,
  chChurchUri TEXT,
  FOREIGN KEY (pubKey) REFERENCES Publication (pubKey) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS ChapterMedia (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pubKey TEXT NOT NULL,
  chSlug TEXT NOT NULL,
  chmType TEXT NOT NULL,
  chmSubType TEXT,
  chmUrl TEXT,
  chmThumbUrl TEXT,
  chmStartSeconds TEXT,
  chmEndSeconds TEXT,
  chmSource TEXT,
  chmChurchAssetId TEXT,
  FOREIGN KEY (pubKey) REFERENCES Publication (pubKey) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Paragraph (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pubKey TEXT NOT NULL,
  chSlug TEXT NOT NULL,
  parPosition INTEGER NOT NULL,
  parType TEXT NOT NULL,
  parId TEXT NOT NULL,
  parContent TEXT NOT NULL,
  parContentHtml TEXT NOT NULL,
  parNumber TEXT,
  parPageNumber TEXT,
  parCompareId TEXT NOT NULL,
  parChurchId TEXT,
  FOREIGN KEY (pubKey) REFERENCES Publication (pubKey) ON DELETE RESTRICT ON UPDATE CASCADE
);

/* INSERT DATA */

{0}

/* CREATE INDEXES */

DROP INDEX IF EXISTS IDX_Publication_pubPosition;
DROP INDEX IF EXISTS IDX_Publication_pubSlug;
DROP INDEX IF EXISTS IDX_Publication_pubVersionSlug;
DROP INDEX IF EXISTS IDX_Chapter_pubKey_chSlug;
DROP INDEX IF EXISTS IDX_Chapter_pubKey_bookSlug;
DROP INDEX IF EXISTS IDX_Chapter_chPosition;
DROP INDEX IF EXISTS FK_Chapter_pubKey;
DROP INDEX IF EXISTS IDX_ChapterMedia_pubKey_chSlug;
DROP INDEX IF EXISTS IDX_ChapterMedia_chmType;
DROP INDEX IF EXISTS FK_ChapterMedia_pubKey;
DROP INDEX IF EXISTS IDX_Paragraph_pubKey_chSlug;
DROP INDEX IF EXISTS IDX_Paragraph_parPosition;
DROP INDEX IF EXISTS IDX_Paragraph_parCompareId;
DROP INDEX IF EXISTS FK_Paragraph_pubKey;
CREATE INDEX IDX_Publication_pubPosition ON Publication (pubPosition);
CREATE INDEX IDX_Publication_pubSlug ON Publication (pubSlug);
CREATE INDEX IDX_Publication_pubVersionSlug ON Publication (pubVersionSlug);
CREATE INDEX IDX_Chapter_pubKey_chSlug ON Chapter (pubKey, chSlug);
CREATE INDEX IDX_Chapter_pubKey_bookSlug ON Chapter (pubKey, bookSlug);
CREATE INDEX IDX_Chapter_chPosition ON Chapter (chPosition);
CREATE INDEX FK_Chapter_pubKey ON Chapter (pubKey);
CREATE INDEX IDX_ChapterMedia_pubKey_chSlug ON ChapterMedia (pubKey, chSlug);
CREATE INDEX IDX_ChapterMedia_chmType ON ChapterMedia (chmType);
CREATE INDEX FK_ChapterMedia_pubKey ON ChapterMedia (pubKey);
CREATE INDEX IDX_Paragraph_pubKey_chSlug ON Paragraph (pubKey, chSlug);
CREATE INDEX IDX_Paragraph_parPosition ON Paragraph (parPosition);
CREATE INDEX IDX_Paragraph_parCompareId ON Paragraph (parCompareId);
CREATE INDEX FK_Paragraph_pubKey ON Paragraph (pubKey);

DROP TABLE IF EXISTS ParagraphFts;
CREATE VIRTUAL TABLE ParagraphFts USING fts4 (
  parContent,
  tokenize=porter
);
INSERT INTO ParagraphFts (docid, parContent) SELECT rowid, parContent FROM Paragraph;

VACUUM;
