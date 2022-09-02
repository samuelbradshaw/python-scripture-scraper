# CONFIGURATION VALUES

# Default language when scraping content (BCP 47)
DEFAULT_LANG = 'en'  # Default: 'en'

# Whether full content should be scraped, in addition to basic metadata (default language only) (warning: scraping full content will send up to 1600 http requests – one for each chapter)
SCRAPE_FULL_CONTENT = True  # Default: True

# Whether basic metadata should be scraped for all languages (if False, only metadata in the default language will be included)
SCRAPE_METADATA_FOR_ALL_LANGUAGES = True  # Default: True

# The script will pause between requests to avoid hitting the Church server too frequently
SECONDS_TO_PAUSE_BETWEEN_REQUESTS = 2  # Default: 2

# Number of spaces to indent in JSON output
JSON_INDENT = 2  # Default: 2

# Whether test data should be used (only includes a subset of chapters)
USE_TEST_DATA = False  # Default: False


# The following values are only applicable when SCRAPE_FULL_CONTENT is True
if SCRAPE_FULL_CONTENT:

  # Full content output format
  OUTPUT_AS_JSON = True  # Default: True
  OUTPUT_AS_HTML = True  # Default: True
  OUTPUT_AS_MD = False  # Default: False
  OUTPUT_AS_TXT = True  # Default: True
  OUTPUT_AS_CSV = False  # Default: False
  OUTPUT_AS_TSV = False  # Default: False
  OUTPUT_AS_SQL_MYSQL = False  # Default: False
  OUTPUT_AS_SQL_SQLITE = False  # Default: False
  
  # Whether output should be split by chapter and put into a nested directory structure (only applicable for JSON output)
  SPLIT_BY_CHAPTER = True  # Default: True
  
  # Whether inline style elements (bold, italics) and hard line breaks should be included
  INCLUDE_INLINE_ELEMENTS = True  # Default: True
  
  # Whether links to images (Abraham facsimiles) should be included
  INCLUDE_IMAGES = True  # Default: True
  
  # Whether links, footnotes, chapter summaries, and other potentially copyrighted content should be included (warning: this is intended for personal use only – copyrighted content should not be distributed online or used in any public or commercial product, without permission from the Church)
  INCLUDE_COPYRIGHTED_CONTENT = False  # Default: False
  
  # Whether a CSS stylesheet should be added to the output files
  ADD_CSS_STYLESHEET = True  # Default: True
