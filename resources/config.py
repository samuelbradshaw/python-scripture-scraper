# CONFIGURATION VALUES

# Default language when scraping content (BCP 47)
DEFAULT_LANG = 'en'  # Default: 'en'

# Whether full content should be scraped, in addition to basic metadata (default language only) (warning: scraping full content will send up to 1600 http requests – one for each chapter)
SCRAPE_FULL_CONTENT = True  # Default: True

# Whether basic metadata should be scraped for all languages (if False, only metadata in the default language will be included)
SCRAPE_METADATA_FOR_ALL_LANGUAGES = False  # Default: False

# The script will pause between requests to avoid hitting the Church server too frequently
SECONDS_TO_PAUSE_BETWEEN_REQUESTS = 1  # Default: 1

# Number of spaces to indent in JSON output
JSON_INDENT = 2  # Default: 2

# Whether test data should be used (only includes a subset of chapters)
USE_TEST_DATA = False  # Default: False


# The following values are only applicable when SCRAPE_FULL_CONTENT is True
if SCRAPE_FULL_CONTENT:

  # Full content output format
  OUTPUT_AS_JSON = True  # Default: True
  OUTPUT_AS_HTML = True  # Default: True
  OUTPUT_AS_MD = True  # Default: True
  OUTPUT_AS_TXT = True  # Default: True
  OUTPUT_AS_CSV = True  # Default: True
  OUTPUT_AS_TSV = True  # Default: True
  OUTPUT_AS_SQL_MYSQL = True  # Default: True
  OUTPUT_AS_SQL_SQLITE = True  # Default: True
  
  # Whether full content output should be split by chapter and put into a nested directory structure (only applicable for JSON output)
  SPLIT_JSON_BY_CHAPTER = True  # Default: True
  
  # Whether full content output should be minified (only applicable for JSON output)
  MINIFY_JSON = False  # Default: False
  
  # Whether spans with CSS classes should be converted to simple HTML tags (only applicable for HTML output)
  BASIC_HTML = False  # Default: False
  
  # Whether links to images (Abraham facsimiles) should be included
  INCLUDE_IMAGES = True  # Default: True
  
  # Whether links, footnotes, chapter summaries, and other potentially copyrighted content should be included (warning: this is intended for personal use only – copyrighted content should not be distributed online or used in any public or commercial product, without permission from the Church)
  INCLUDE_COPYRIGHTED_CONTENT = False  # Default: False
  
  # Whether audio, video, PDF, and other related media information should be included (requires Playwright for Python, and may run a little slower). You can install Playwright by running these commands in Terminal:
  # pip3 install pytest-playwright
  # playwright install
  INCLUDE_MEDIA_INFO = False  # Default: False
  
  # Whether a CSS stylesheet should be added to the output files
  ADD_CSS_STYLESHEET = True  # Default: True
