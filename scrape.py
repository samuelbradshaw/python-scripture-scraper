# Python standard libraries
import os
import sys
import shutil
import json
import csv
from datetime import date, datetime
import time
import copy
import re

# Third-party libraries
import requests
from bs4 import BeautifulSoup, Tag
from markdownify import MarkdownConverter, markdownify

# Internal imports
from resources import resources, config

# python-scripture-scraper version
VERSION = '2.0'

# URL patterns
languages_url = 'https://www.churchofjesuschrist.org/languages?lang=eng'
study_url = 'https://www.churchofjesuschrist.org/study{0}?lang={1}&mboxDisable=1'
abbreviations_url = 'https://www.churchofjesuschrist.org/study/scriptures/quad/quad/abbreviations?lang={0}&mboxDisable=1'

working_directory = os.path.abspath(os.path.dirname(__file__))
output_directory = os.path.join(working_directory, '_output')

skipped_languages = set()
incomplete_publications = set()

date_today = date.today()

metadata_languages = {
  '_about': 'Generated {0} by Python Scripture Scraper (https://github.com/samuelbradshaw/python-scripture-scraper)'.format(date_today),
  'languages': {},
  'mapToBcp47': {},
}

metadata_scriptures = {
  '_about': 'Generated {0} by Python Scripture Scraper (https://github.com/samuelbradshaw/python-scripture-scraper)'.format(date_today),
  'languages': {},
  'mapToSlug': {},
  'structure': {},
}

metadata_scriptures_language_template = {
  'punctuation': {
    'bookChapterSeparator': ' ',
    'chapterVerseSeparator': ':',
    'verseRangeSeparator': '–',
    'verseGroupSeparator': ', ',
    'referenceSeparator': '; ',
  },
  'numerals': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
  'translatedNames': {},
  'churchAvailability': {
    'old-testament': [],
    'new-testament': [],
    'book-of-mormon': [],
    'doctrine-and-covenants': [],
    'pearl-of-great-price': [],
  },
}

metadata_uri_to_name = {
  '_about': 'Generated {0} by Python Scripture Scraper (https://github.com/samuelbradshaw/python-scripture-scraper)'.format(date_today),
}

def main():
  # Create an empty output directory
  shutil.rmtree(output_directory, ignore_errors=True)
  os.makedirs(output_directory)
  
  global metadata_structure
  global languages
    
  if config.USE_TEST_DATA:
    # Use test data (only includes a subset of chapters)
    metadata_structure = resources.test_data_structure
    languages = get_languages([config.DEFAULT_LANG, 'en'])    
    
  else:
    metadata_structure = resources.metadata_structure
    
    # Get list of languages
    if config.SCRAPE_METADATA_FOR_ALL_LANGUAGES:
      languages = get_languages()
    else:
      languages = get_languages([config.DEFAULT_LANG])
    
  metadata_scriptures['structure'] = metadata_structure
  
  # Gather metadata for each language
  for language in languages:
    time.sleep(config.SECONDS_TO_PAUSE_BETWEEN_REQUESTS)
    gather_metadata_for_language(language)
  
  # Print language metadata warnings
  if skipped_languages:
    sys.stdout.write('Skipped {0} language{1} without scripture data ({2})\n'.format(len(skipped_languages), 's'[:len(skipped_languages)^1], ', '.join(sorted(skipped_languages))))
  if incomplete_publications:
    sys.stdout.write('{0} publication{1} with missing books ({2})\n'.format(len(incomplete_publications), 's'[:len(incomplete_publications)^1], ', '.join(sorted(incomplete_publications))))
  sys.stdout.write('\n')

  # Create metadata files
  sys.stdout.write('Creating metadata-languages.json\n')
  with open(os.path.join(output_directory, 'metadata-languages.json'), 'w', encoding='utf-8') as f:
    json.dump(metadata_languages, fp=f, indent=config.JSON_INDENT, separators=(', ', ': '), ensure_ascii=False, sort_keys=False)
  with open(os.path.join(output_directory, 'metadata-languages.min.json'), 'w', encoding='utf-8') as f:
    json.dump(metadata_languages, fp=f, indent=None, separators=(',', ':'), ensure_ascii=False, sort_keys=False)

  sys.stdout.write('Creating metadata-scriptures.json\n')
  metadata_scriptures['mapToSlug'] = dict(sorted(metadata_scriptures['mapToSlug'].items()))
  with open(os.path.join(output_directory, 'metadata-scriptures.json'), 'w', encoding='utf-8') as f:
    json.dump(metadata_scriptures, fp=f, indent=config.JSON_INDENT, separators=(', ', ': '), ensure_ascii=False, sort_keys=False)
  with open(os.path.join(output_directory, 'metadata-scriptures.min.json'), 'w', encoding='utf-8') as f:
    json.dump(metadata_scriptures, fp=f, indent=None, separators=(',', ':'), ensure_ascii=False, sort_keys=False)

  sys.stdout.write('Creating metadata-uri-to-name.json\n')
  with open(os.path.join(output_directory, 'metadata-uri-to-name.json'), 'w', encoding='utf-8') as f:
    json.dump(metadata_uri_to_name, fp=f, indent=config.JSON_INDENT, separators=(', ', ': '), ensure_ascii=False, sort_keys=True)
  with open(os.path.join(output_directory, 'metadata-uri-to-name.min.json'), 'w', encoding='utf-8') as f:
    json.dump(metadata_uri_to_name, fp=f, indent=None, separators=(',', ':'), ensure_ascii=False, sort_keys=True)
  
  if config.SCRAPE_FULL_CONTENT:
    # Output full content
    sys.stdout.write('\n')
    output_full_content(config.DEFAULT_LANG)
    
    if config.ADD_CSS_STYLESHEET:
      # Output CSS stylesheet
      sys.stdout.write('Creating styles.css\n\n')
      css_path = os.path.join(output_directory, 'styles.css')
      with open(css_path, 'w', encoding='utf-8') as f:
        f.write(resources.css_template)

  # Create README for output files
  sys.stdout.write('Creating README.txt\n')
  config_string = ''
  for (key, value) in config.__dict__.items():
    if not callable(getattr(config, key)) and not key.startswith('__'):
      if isinstance(value, str):
        value = '\'' + value + '\''
      config_string += '{0} = {1}\n'.format(key, value)
  info = resources.readme_template.format(VERSION, datetime.now(), config_string)
  readme_path = os.path.join(output_directory, 'README.txt')
  with open(readme_path, 'w', encoding='utf-8') as f:
    f.write(info)

  sys.stdout.write('\nDone!\n\n')


# Get the list of available languages
def get_languages(selected_langs=None):
  sys.stdout.write('\nGetting languages\n')
  languages = []
  
  # Fetch the languages page
  r = requests.get(languages_url)
  r.encoding = 'utf-8'
  if r and r.status_code == 200:

    # Parse the languages page
    soup = BeautifulSoup(r.text, 'html.parser')
    language_links = soup.select('.language-list a[data-lang]')
    for link in language_links:
      church_lang = link.attrs['data-lang']
      try:
        bcp47_lang = resources.mapping_church_lang_to_bcp47[church_lang]
      except:
        print_warning('Warning: Language “{0}” is not recognized and will be ignored (most likely it was added to Church content recently). To include this language, add it to the language mappings in resources.py.\n'.format(church_lang))
        continue
      autonym = link.text
      name = re.match(r'^.*\((.+)\).*$', link.attrs['title'], flags=re.DOTALL).group(1).strip()
      if not selected_langs or bcp47_lang in selected_langs:
      
        # Add language to the languages list
        languages.append({
          'bcp47_lang': bcp47_lang,
          'church_lang': church_lang,
          'autonym': autonym,
          'name': name,
        })
  else:
    sys.exit('Error: Unable to connect to {0}'.format(languages_url))
  
  sys.stdout.write('Found {0} language{1}\n\n'.format(len(languages), 's'[:len(languages)^1]))
  
  sorted_languages = sorted(languages, key=lambda l: l['bcp47_lang'])
  return sorted_languages


# Get publication version info
def get_version_info(bcp47_lang, publication_slug, publication_uri):
      
  # Get Bible version info from resources.py
  bible_version_info = (resources.bible_version_info.get(bcp47_lang) or {}).get(publication_slug)
  if publication_slug in ('old-testament', 'new-testament',) and not bible_version_info:
    print_warning('Warning: Bible info is missing in resources.py for {0}/{1}.\n'.format(bcp47_lang, publication_slug))
  
  version_info = bible_version_info or {
    'versionKey': None,
    'versionAbbrev': None,
    'versionName': None,
    'editionYear': None,
    'firstEditionYear': None,
    'copyrightStatement': None,
    'copyrightOwner': None,
  }
  
  # Add copyright info for Church-owned content
  if publication_slug not in ('old-testament', 'new-testament',):
    version_info['copyrightOwner'] = 'iri'
    
    # Scrape copyright info from title page
    time.sleep(config.SECONDS_TO_PAUSE_BETWEEN_REQUESTS)
    study_uri = publication_uri + '/title-page'
    r = requests.get(study_url.format(study_uri, metadata_languages['languages'][bcp47_lang]['churchLang']))
    r.encoding = 'utf-8'
    if r and r.status_code == 200:
      soup = BeautifulSoup(r.text, 'html.parser')
      copyright_info = soup.select_one('.copyright-info > p')
      if copyright_info:
        copyright_info_text = copyright_info.text.strip()
        if copyright_info_text:
          version_info['copyrightStatement'] = copyright_info_text
          copyright_year_matches = re.search(r'©.*?(\d{4})', copyright_info_text)
          if copyright_year_matches:
            version_info['editionYear'] = copyright_year_matches.group(1)
    
    # Add generic copyright statement if scraping failed
    if not version_info.get('copyrightStatement'):
      version_info['copyrightStatement'] = '© by Intellectual Reserve, Inc.'
    
    # Get first edition info from resources.py
    version_info['firstEditionYear'] = (resources.first_edition_years.get(bcp47_lang) or {}).get(publication_slug)
    if not version_info.get('firstEditionYear'):
      print_warning('Warning: First edition year is missing in resources.py for {0}/{1}.\n'.format(bcp47_lang, publication_slug))
  
  # Override copyright info if copyrighted content was removed
  if bcp47_lang == 'en' and config.SCRAPE_FULL_CONTENT and not config.INCLUDE_COPYRIGHTED_CONTENT:
    version_info['copyrightStatement'] = 'Public domain (copyrighted portions removed).'
    version_info['copyrightOwner'] = 'pd'

  return version_info


# Gather metadata for an individual language
def gather_metadata_for_language(language):
  available_uris = []
  bcp47_lang = language['bcp47_lang']
  
  # Fetch the root scriptures page to see what exists in the language
  r = requests.get(study_url.format('/scriptures', language['church_lang']))
  r.encoding = 'utf-8'
  if r and r.status_code == 200:
    sys.stdout.write('Gathering metadata: {0} / {1} / {2}\n'.format(language['bcp47_lang'], language['autonym'], language['name']))
    
    # Parse the scriptures page
    soup = BeautifulSoup(r.text, 'html.parser')
    available_uris = [a.attrs['href'].split('?')[0].replace('/study/', '/') for a in soup.select('#main a[href]')]

  else:
    # If no scriptures exist, skip the language
    skipped_languages.add(bcp47_lang)
    return
  
  # Add language to metadata_languages dictionary
  current_language = [l for l in languages if l['bcp47_lang'] == bcp47_lang][0]
  metadata_languages['languages'][bcp47_lang] = {
    'name': current_language['name'],
    'autonym': current_language['autonym'],
    'churchLang': current_language['church_lang'],
  }
  metadata_languages['mapToBcp47'][bcp47_lang] = bcp47_lang
  metadata_languages['mapToBcp47'][current_language['church_lang']] = bcp47_lang
  
  # Add language to metadata_scriptures dictionary
  metadata_scriptures['languages'][bcp47_lang] = copy.deepcopy(metadata_scriptures_language_template)
    
  # Get localized punctuation and numerals
  if bcp47_lang in ('en', 'ase',):
    # Use defaults
    pass
  elif bcp47_lang == 'am':
    # Python regex doesn't recognize Amharic numerals correctly, so these values are hard-coded
    metadata_scriptures['languages'][bcp47_lang]['punctuation'] = {
      'bookChapterSeparator': ' ',
      'chapterVerseSeparator': '፥',
      'verseRangeSeparator': '–',
      'verseGroupSeparator': '፣ ',
      'referenceSeparator': '፤ ',
    }
    # Amharic numerals can't be translated 1 to 1 with English numerals
    metadata_scriptures['languages'][bcp47_lang]['numerals'] = None
  elif '/scriptures/bofm' in available_uris:
    # Other languages: Parse examples from 1 Nephi 1
    study_uri = '/scriptures/bofm/1-ne/1'
    time.sleep(config.SECONDS_TO_PAUSE_BETWEEN_REQUESTS)
    r = requests.get(study_url.format(study_uri, language['church_lang']))
    r.encoding = 'utf-8'
    if r and r.status_code == 200:
      soup = BeautifulSoup(r.text, 'html.parser')
      footnotes = soup.select_one('.study-notes')
      if soup.select_one('#content article').attrs['data-uri'] == study_uri:
        if footnotes:
          verse_range_separator_example = footnotes.select_one('#note1d_p1 a, #note1_d_p1 a').find_next_sibling('a').text  # 'Mosiah 1:2–3'
          verse_group_separator_example = footnotes.select_one('#note1c_p1 a, #note1_c_p1 a').text  # 'D&C 68:25, 28'
          reference_separator = footnotes.select_one('#note1d_p1 a, #note1_d_p1 a').next_sibling.text  # '; '
          metadata_scriptures['languages'][bcp47_lang]['punctuation']['bookChapterSeparator'] = re.match(r'^[^\s]+(.*?)\d+', verse_range_separator_example).group(1)
          metadata_scriptures['languages'][bcp47_lang]['punctuation']['chapterVerseSeparator'] = re.match(r'^.+?\d+(.+?)\d+', verse_range_separator_example).group(1)
          metadata_scriptures['languages'][bcp47_lang]['punctuation']['verseRangeSeparator'] = re.match(r'^.+?\d+.+?\d+(.+?)\d+', verse_range_separator_example).group(1)
          try:
            metadata_scriptures['languages'][bcp47_lang]['punctuation']['verseGroupSeparator'] = re.match(r'^.+?\d+.+?\d+(.+?)\d+', verse_group_separator_example).group(1)
          except:
            # In Indonesian and possibly other languages, the word order is reversed, so use footnote b instead of footnote c
            verse_group_separator_example = footnotes.select_one('#note1b_p1 a, #note1_b_p1 a').text  # 'D&C 68:25, 28'
            metadata_scriptures['languages'][bcp47_lang]['punctuation']['verseGroupSeparator'] = re.match(r'^.+?\d+.+?\d+(.+?)\d+', verse_group_separator_example).group(1)
          metadata_scriptures['languages'][bcp47_lang]['punctuation']['referenceSeparator'] = reference_separator
        verse_number_spans = soup.select('.verse-number')  # '1 ', '2 ', '3 ', etc.
        if verse_number_spans:
          verse_numbers = [re.match(r'(\d+)', span.text).group(1) for span in verse_number_spans]
          metadata_scriptures['languages'][bcp47_lang]['numerals'] = [verse_numbers[9].replace(verse_numbers[0], '')] + verse_numbers[:9]
    else:
      sys.exit('Error: Unable to connect to {0}'.format(study_url.format(study_uri, language['church_lang'])))

  # Attempt to get book names and abbreviations from "Abbreviations" content
  if '/scriptures/study-helps' in available_uris:
  
    # Fetch the abbreviations page, if it exists
    time.sleep(config.SECONDS_TO_PAUSE_BETWEEN_REQUESTS)
    r = requests.get(abbreviations_url.format(language['church_lang']))
    r.encoding = 'utf-8'
    if r and r.status_code == 200:
      soup = BeautifulSoup(r.text, 'html.parser')
      rows = soup.select('figure table tr')
      
      # Loop through known scripture structure and the list of abbreviations, and map them to each other
      book_counter = 0
      for pub, (publication_slug, publication_data) in enumerate(resources.metadata_structure.items()):
        publication_name = soup.select_one('#figure{0}_title1'.format(pub+1)).text.strip()
        publication_uri = publication_data['churchUri']
        
        # Add publication name to metadata_uri_to_name and metadata_scriptures
        if publication_uri not in metadata_uri_to_name:
          metadata_uri_to_name[publication_uri] = {}
        if publication_slug not in metadata_scriptures['languages'][bcp47_lang]['translatedNames']:
          metadata_scriptures['languages'][bcp47_lang]['translatedNames'][publication_slug] = metadata_uri_to_name[publication_uri][bcp47_lang] = {
            'name': publication_name,
            'abbrev': None,
          }
          metadata_scriptures['mapToSlug'][publication_name] = publication_slug
        
        for book_slug, book_data in publication_data['books'].items():
          if not book_data.get('churchUri'):
            continue
          
          book_row = rows[book_counter]
          book_name = book_row.select('td')[1].text.strip()
          book_abbreviation = book_row.select('td')[0].text.strip()
          
          # Add book name and abbreviation to metadata_uri_to_name and metadata_scriptures
          if book_data['churchUri'] not in metadata_uri_to_name:
            metadata_uri_to_name[book_data['churchUri']] = {}
          if book_slug not in metadata_scriptures['languages'][bcp47_lang]['translatedNames']:
            metadata_scriptures['languages'][bcp47_lang]['translatedNames'][book_slug] = metadata_uri_to_name[book_data['churchUri']][bcp47_lang] = {
              'name': book_name,
              'abbrev': book_abbreviation,
            }
            metadata_scriptures['mapToSlug'][book_name] = book_slug
            metadata_scriptures['mapToSlug'][book_abbreviation] = book_slug
          
          book_counter += 1
      
      # Get names and abbreviations for study helps
      for r, row in enumerate(soup.select('#figure6 table tr')):
        if bcp47_lang == 'en':
          if r == 0:
            book_slug = 'joseph-smith-translation'
            book_uri = '/scriptures/jst'
          elif r == 1:
            book_slug = 'topical-guide'
            book_uri = '/scriptures/tg'
          elif r == 2:
            book_slug = 'bible-dictionary'
            book_uri = '/scriptures/bd'
          elif r == 3:
            book_slug = 'index-to-the-triple-combination'
            book_uri = '/scriptures/triple-index'
          elif r == 4:
            book_slug = 'guide-to-the-scriptures'
            book_uri = '/scriptures/gs'
          else:
            continue
        else:
          if r == 0:
            book_slug = 'joseph-smith-translation'
            book_uri = '/scriptures/jst'
          elif r == 1:
            book_slug = 'guide-to-the-scriptures'
            book_uri = '/scriptures/gs'
          else:
            continue
        
        book_name = row.select('td')[1].text.strip()
        book_abbreviation = row.select('td')[0].text.strip()
        
        # Add book name and abbreviation to metadata_uri_to_name and metadata_scriptures
        if book_uri not in metadata_uri_to_name:
          metadata_uri_to_name[book_uri] = {}
        if book_slug not in metadata_scriptures['languages'][bcp47_lang]['translatedNames']:
          metadata_scriptures['languages'][bcp47_lang]['translatedNames'][book_slug] = metadata_uri_to_name[book_uri][bcp47_lang] = {
            'name': book_name,
            'abbrev': book_abbreviation,
          }
          metadata_scriptures['mapToSlug'][book_name] = book_slug
          metadata_scriptures['mapToSlug'][book_abbreviation] = book_slug
  
  # Get book availability (and names if not fetched above) from the scripture publication table of contents
  for publication_slug, publication_data in metadata_structure.items():
    publication_uri = publication_data['churchUri']
    if publication_uri in available_uris:
      time.sleep(config.SECONDS_TO_PAUSE_BETWEEN_REQUESTS)
      r = requests.get(study_url.format(publication_uri, language['church_lang']))
      r.encoding = 'utf-8'
      if r and r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        table_of_contents = soup.select_one('#content .body')
        publication_name = table_of_contents.select_one('header').text.strip()
        
        # Add publication name to metadata_uri_to_name and metadata_scriptures
        if publication_uri not in metadata_uri_to_name:
          metadata_uri_to_name[publication_uri] = {}
        if publication_slug not in metadata_scriptures['languages'][bcp47_lang]['translatedNames']:
          metadata_scriptures['languages'][bcp47_lang]['translatedNames'][publication_slug] = metadata_uri_to_name[publication_uri][bcp47_lang] = {
            'name': publication_name,
            'abbrev': None,
          }
          metadata_scriptures['mapToSlug'][publication_name] = publication_slug
    
        for book_slug, book_data in publication_data['books'].items():
          
          # Get the first chapter link (from the scripture publication's table of contents) that contains the book URI
          first_chapter_link = table_of_contents.select_one('a.list-tile[href^="/study{0}"]'.format(book_data['churchUri']))
          if not first_chapter_link:
            # If book is missing from the publication (selections, or progressive publishing), skip it
            if book_data.get('churchUri'):
              incomplete_publications.add('{0}/{1}'.format(bcp47_lang, publication_slug))
            continue
          
          # Update availability data
          metadata_scriptures['languages'][bcp47_lang]['churchAvailability'][publication_slug].append(book_slug)
          
          # Get the book name by looking for the preceding title
          previous_title = first_chapter_link.find_previous(class_='title')
          book_name = previous_title.text.strip()
          
          # If the previous element is a list item, the chapter link title is the book title (single-chapter book like Enos)
          if first_chapter_link.parent.find_previous_sibling('li'):
            book_name = first_chapter_link.select_one('.title').text.strip()
        
          # Add book name to metadata_uri_to_name and metadata_scriptures
          if book_data['churchUri'] not in metadata_uri_to_name:
            metadata_uri_to_name[book_data['churchUri']] = {}
          if book_slug not in metadata_scriptures['languages'][bcp47_lang]['translatedNames']:
            metadata_scriptures['languages'][bcp47_lang]['translatedNames'][book_slug] = metadata_uri_to_name[book_data['churchUri']][bcp47_lang] = {
              'name': book_name,
              'abbrev': None,
            }
            metadata_scriptures['mapToSlug'][book_name] = book_slug
            
  # Get singular book names: psalm, section, official-declaration
  study_uri = '/manual/come-follow-me-for-individuals-and-families-old-testament-2022/33'
  time.sleep(config.SECONDS_TO_PAUSE_BETWEEN_REQUESTS)
  r = requests.get(study_url.format(study_uri, language['church_lang']))
  r.encoding = 'utf-8'
  if r and r.status_code == 200:
    soup = BeautifulSoup(r.text, 'html.parser')
    psalm_example = soup.select_one(f'#p9 a.scripture-ref[href^="/study/scriptures/ot/ps/2?"]').text  # 'Psalm 2'
    try:
      psalm_name = re.match(r'(.+?)\d+', psalm_example).group(1).strip()
    except:
      # Some languages, like Latvian, put the number first for Psalm (2. psalmā) or Section (1. nodaļa)
      psalm_name = re.match(r'\d+\.*(.+)', psalm_example).group(1).strip()
    metadata_scriptures['languages'][bcp47_lang]['translatedNames']['psalm'] = {
      'name': psalm_name,
      'abbrev': metadata_scriptures['languages'][bcp47_lang]['translatedNames'].get('psalms', {}).get('abbrev'),
    }
    metadata_scriptures['mapToSlug'][psalm_name] = 'psalm'      
  if '/scriptures/dc-testament' in available_uris:
    study_uri = '/scriptures/dc-testament/dc/1'
    time.sleep(config.SECONDS_TO_PAUSE_BETWEEN_REQUESTS)
    r = requests.get(study_url.format(study_uri, language['church_lang']))
    r.encoding = 'utf-8'
    if r and r.status_code == 200:
      soup = BeautifulSoup(r.text, 'html.parser')
      section_example = soup.select_one(f'p[id="title_number1"]').text  # 'Section 1'
      try:
        section_name = re.match(r'(.+?)(?:\d|Ⅰ|፩|一)+', section_example).group(1).strip()
      except:
        section_name = re.match(r'\d+\.*(.+)', section_example).group(1).strip()
      metadata_scriptures['languages'][bcp47_lang]['translatedNames']['section'] = {
        'name': section_name,
        'abbrev': metadata_scriptures['languages'][bcp47_lang]['translatedNames'].get('sections', {}).get('abbrev'),
      }
      metadata_scriptures['mapToSlug'][section_name] = 'section'
      try:
        official_declaration_example = soup.select_one('a[href^="/study/scriptures/dc-testament/od/1"]').text  # 'Official Declaration 1'
        try:
          official_declaration_name = re.match(r'(.+?)(?:\d|Ⅰ|፩|一)+', official_declaration_example).group(1).strip()
        except:
          official_declaration_name = re.match(r'\d+\.*(.+)', official_declaration_example).group(1).strip()
        metadata_scriptures['languages'][bcp47_lang]['translatedNames']['official-declaration'] = {
          'name': official_declaration_name,
          'abbrev': metadata_scriptures['languages'][bcp47_lang]['translatedNames'].get('official-declarations', {}).get('abbrev'),
        }
        metadata_scriptures['mapToSlug'][official_declaration_name] = 'official-declaration'      
      except:
        # Some languages, like Guaraní, don't have Official Declarations translated yet
        pass
  
  # Get names of named chapters: fac-1, fac-2, fac-3
  if '/scriptures/pgp' in available_uris:
    study_uri = '/scriptures/pgp/abr'
    time.sleep(config.SECONDS_TO_PAUSE_BETWEEN_REQUESTS)
    r = requests.get(study_url.format(study_uri, language['church_lang']))
    r.encoding = 'utf-8'
    if r and r.status_code == 200:
      soup = BeautifulSoup(r.text, 'html.parser')
      chapter_titles = soup.select(f'a.list-tile[href^="/study{study_uri}/fac"]')
      if chapter_titles:
        # Some languages, like Hawaiian, don't have Abraham Facsimiles translated yet
        metadata_scriptures['languages'][bcp47_lang]['translatedNames']['fac-1'] = {
          'name': chapter_titles[0].text,
          'abbrev': None,
        }
        metadata_scriptures['languages'][bcp47_lang]['translatedNames']['fac-2'] = {
          'name': chapter_titles[1].text,
          'abbrev': None,
        }
        metadata_scriptures['languages'][bcp47_lang]['translatedNames']['fac-3'] = {
          'name': chapter_titles[2].text,
          'abbrev': None,
        }
        metadata_scriptures['mapToSlug'][chapter_titles[0].text] = 'fac-1'
        metadata_scriptures['mapToSlug'][chapter_titles[1].text] = 'fac-2'
        metadata_scriptures['mapToSlug'][chapter_titles[2].text] = 'fac-3'

  return    


# Scrape full content for a given language
def output_full_content(bcp47_lang):
  all_publications_dict_list = []
  all_chapters_dict_list = []
  all_chapter_media_dict_list = []
  all_paragraphs_dict_list = []
  
  # Get the type for a given paragraph
  def get_paragraph_type(paragraph):
    type = 'paragraph'
    if paragraph.name == 'h1':
      type = 'book-title'
    elif paragraph.get('id') == 'title_number1':
      type = 'chapter-title'
    elif paragraph.get('id') == 'subtitle1':
      if isinstance(paragraph.previous_sibling, Tag):
        previous_element_sibling = paragraph.previous_sibling
      else:
        previous_element_sibling = paragraph.previous_sibling.previous_sibling
      if previous_element_sibling.name == 'h1':
        type = 'book-subtitle'
      elif previous_element_sibling.get('id') == 'title_number1':
        type = 'chapter-subtitle'
    elif paragraph.name == 'h2':
      type = 'section-title'
    elif paragraph.get('class') and paragraph.get('class')[0] == 'verse':
      type = 'verse'
    elif paragraph.get('class') and paragraph.get('class')[0] == 'study-intro':
      type = 'study-paragraph'
    elif paragraph.get('class') and paragraph.get('class')[0] == 'study-summary':
      type = 'study-paragraph'
    elif paragraph.name == 'img':
      type = 'image'
    elif paragraph.name == 'ul':
      type = 'study-footnotes'
    return type
  
  # Get the id for a given paragraph
  paragraph_type_data_by_chapter = {}
  def get_paragraph_id(chapter_slug, paragraph_type):
    if not chapter_slug in paragraph_type_data_by_chapter:
      paragraph_type_data_by_chapter[chapter_slug] = []
    paragraph_type_data_by_chapter[chapter_slug].append(paragraph_type)
    paragraph_type_count = paragraph_type_data_by_chapter[chapter_slug].count(paragraph_type)
    paragraph_type_abbrev = resources.mapping_paragraph_type_to_paragraph_type_abbrev.get(paragraph_type)
    return f'{paragraph_type_abbrev}{paragraph_type_count}'
  
  # Get the number for a given paragraph
  def get_paragraph_number(paragraph):
    number = None
    number_span = paragraph.select_one('.verse-number')
    if number_span:
      number = number_span.text.strip()
    return number
  
  # Get the content for a given paragraph (content_type: text, html, or markdown)
  def get_paragraph_content(paragraph, content_type='text', basic_html=config.BASIC_HTML, include_number=False, id_prefix='', id=''):
    content = ''
    paragraph_type = get_paragraph_type(paragraph)

    if content_type in ('text', 'markdown'):
      basic_html = True
    
    # Image paragraph type
    if paragraph_type == 'image':
      image_asset_id = paragraph.get('data-assetid')
      image_alt = paragraph.get('alt', '')
      image_filename = (paragraph.get('src') or '').split('/')[-1]
      if image_asset_id and image_filename:
        image_url = 'https://assets.ldscdn.org/{0}/{1}/{2}/{3}'.format(image_asset_id[0:2], image_asset_id[2:4], image_asset_id, image_filename)
        if content_type == 'html':
          content = '<img id="{0}{1}" src="{2}" alt="{3}" data-asset-id="{4}" loading="lazy" decoding="async">'.format(id_prefix, id, image_url, image_alt, image_asset_id)
        elif content_type == 'markdown':
          '![{0}]({1})'.format(image_alt, image_url)
        else:
          content = image_url
      return content
    
    # Copy the paragraph to avoid modifying the original
    temp_paragraph = copy.copy(paragraph)
    
    # Remove verse number if needed
    number_span = temp_paragraph.select_one('.verse-number')
    if number_span and not include_number:
      number_span.decompose()
    
    # Normalize superscript and footnotes
    for element in temp_paragraph.select('.study-note-ref sup'):
      marker_value = element.text or element.get('data-value')
      if basic_html and element.get('data-value'):
        element.attrs.pop('data-value')
        element.string = marker_value
      else:
        element['data-value'] = marker_value
        element.string = ''
    for element in temp_paragraph.select('.study-note-ref'):
      element['class'] = 'footnote-link'
      element.attrs.pop('data-scroll-id')
    
    # Add prefix to element IDs if needed
    if content_type in ('html', 'markdown',) and id_prefix:
      for element in temp_paragraph.select('[id]'):
        element.attrs['id'] = id_prefix + element.attrs['id']
      for element in temp_paragraph.select('[href^="#"]'):
        element.attrs['href'] = element.attrs['href'].replace('#', f'#{id_prefix}', 1)
    
    if basic_html:
      # Convert text to uppercase, replace spans with simple style tags
      selectors_to_convert_to_uppercase = '.small-caps, .uppercase'
      for element in temp_paragraph.select(selectors_to_convert_to_uppercase):
        element.string = element.text.upper()
        element.unwrap()
      for element in temp_paragraph.select('.verse-number'):
        element.name = 'b'
        element.attrs.pop('class')
      for element in temp_paragraph.select('.clarity-word'):
        element.name = 'i'
        element.attrs.pop('class')
    
    if content_type == 'markdown':
      # Markdown content
      # Add anchors
      for element in temp_paragraph.select('[id]'):
        element_id = element.get('id')
        element.insert(0, f'<a name="{element_id}"></a>')
      content = MarkdownConverter(escape_underscores=False).convert_soup(temp_paragraph)
    elif content_type == 'html':
      # HTML content
      content = temp_paragraph.decode_contents().replace(' </small>', '</small> ').strip()
    else:
      # Plain text
      # Remove superscript and footnotes
      for element in temp_paragraph.select('sup'):
        element.decompose()
      if temp_paragraph.get('class') and temp_paragraph.get('class')[0] == 'footnotes':
        return ''
      content = temp_paragraph.text.strip()
    
    # Remove extra line breaks
    content = content.replace('\n\n\n', '\n\n').replace('\n\n\n', '\n\n').replace('\n\n\n', '\n\n').replace('\n\n\n', '\n\n')
    
    return content
  
  # Loop through each publication of scripture
  for publication_slug, publication_data in metadata_structure.items():
    if metadata_scriptures['languages'][bcp47_lang]['churchAvailability'][publication_slug]:
      chapters_in_publication_count = 0
      json_content = {}
      html_content = ''
      md_content = ''
      txt_content = ''
      
      version_info = get_version_info(bcp47_lang, publication_slug, publication_data['churchUri'])
      publication_key = '_'.join(filter(None, [bcp47_lang, publication_data['abbrev'], version_info['versionKey'] or version_info['editionYear']]))
      publication_version_slug = publication_slug + ('-'+version_info['versionKey'] if version_info['versionKey'] else '')
      
      if config.OUTPUT_AS_CSV or config.OUTPUT_AS_TSV or config.OUTPUT_AS_SQL_MYSQL or config.OUTPUT_AS_SQL_SQLITE:
        all_publications_dict_list.append({
          'pubKey': publication_key,
          'langBcp47': bcp47_lang,
          'pubPosition': len(all_publications_dict_list),
          'pubSlug': publication_slug,
          'pubName': metadata_scriptures['languages'][bcp47_lang]['translatedNames'][publication_slug]['name'],
          'pubVersionSlug': publication_version_slug,
          'pubVersionAbbrev': version_info['versionAbbrev'],
          'pubVersionName': version_info['versionName'],
          'pubEditionYear': version_info['editionYear'],
          'pubFirstEditionYear': version_info['firstEditionYear'],
          'pubCopyrightStatement': version_info['copyrightStatement'],
          'pubCopyrightOwner': version_info['copyrightOwner'],
          'pubCategory': 'bible' if publication_slug in ('old-testament', 'new-testament',) else 'cjc',
          'pubIsHistorical': 0,
          'pubIsManuscript': 0,
          'pubSource': 'ChurchofJesusChrist.org',
          'pubSourceUrl': 'https://www.churchofjesuschrist.org/study/scriptures?lang=' + resources.mapping_bcp47_to_church_lang[bcp47_lang],
          'pubChurchUri': publication_data['churchUri'],
        })
      
      for book_slug, book_data in publication_data['books'].items():
        if book_slug in metadata_scriptures['languages'][bcp47_lang]['churchAvailability'][publication_slug] and book_data.get('churchUri'):
          sys.stdout.write('Scraping {0} ({1})\n'.format(metadata_scriptures['languages'][bcp47_lang]['translatedNames'][book_slug]['name'], book_slug))
        else:
          continue
        
        previous_page_number = None
        for chapter in book_data['churchChapters']:
          chapter_number = str(chapter)
          singular_book_slug = resources.mapping_plural_to_singular_book_slug.get(book_slug) or book_slug
          chapter_slug = '{0}-{1}'.format(singular_book_slug, chapter_number)
          chapter_uri = '{0}/{1}'.format(book_data['churchUri'], chapter_number)
      
          # Get chapter content
          soup = None
          time.sleep(config.SECONDS_TO_PAUSE_BETWEEN_REQUESTS)
          if config.INCLUDE_MEDIA_INFO:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as pw:
              browser = pw.chromium.launch(headless=True)
              page = browser.new_page()
              page.goto(study_url.format(chapter_uri, resources.mapping_bcp47_to_church_lang[bcp47_lang]))
              if page.query_selector('#content article[data-uri="{0}"]'.format(chapter_uri)):
                page.locator('[data-testid="options-tab"]').click()
                page.locator('[data-testid="download-menu-label"]').click()
                page.wait_for_selector('[data-testid="downloads-panel-header"]')
                full_html = page.content()
                soup = BeautifulSoup(full_html, 'html.parser')
              else:
                print_warning('Warning: Loaded page doesn’t match expected URI: {0}\n'.format(chapter_uri))
              page.close()
              browser.close()
          else:
            r = requests.get(study_url.format(chapter_uri, resources.mapping_bcp47_to_church_lang[bcp47_lang]))
            r.encoding = 'utf-8'
            if r and r.status_code == 200:
              soup = BeautifulSoup(r.text, 'html.parser')
              if not soup.select_one('#content article[data-uri="{0}"]'.format(chapter_uri)):
                print_warning('Warning: Loaded page doesn’t match expected URI: {0}\n'.format(chapter_uri))
          
          if soup:
            content = soup.select_one('#content')            
            
            # Get media info
            chapter_media = []
            video_element = content.select_one('header video')
            downloads_element = soup.select_one('[data-testid="download-panel-content"]')
            if video_element:
              for source in video_element.select('source'):
                if source.get('data-src'):
                  subtype = None
                  if 'hls.m3u8' in source.get('data-src'):
                    subtype = 'hls'
                  elif source.get('data-height') == '360':
                    subtype = '360p'
                  elif source.get('data-height') == '720':
                    subtype = '720p'
                  elif source.get('data-height') == '1080':
                    subtype = '1080p'
                  chapter_media.append({
                    'type': 'video',
                    'subtype': subtype,
                    'url': source.get('data-src'),
                    'id': video_element.get('data-assetid'),
                    'thumbUrl': video_element.get('data-poster'),
                    'startSeconds': None,
                    'endSeconds': None,
                    'source': 'ChurchofJesusChrist.org',
                  })
            if downloads_element:
              for link in downloads_element.select('a'):
                if link.get('href') and not 'Entire' in link.text:
                  media_type = None
                  if 'MP3' in link.text:
                    media_type = 'audio'
                  elif 'PDF' in link.text:
                    media_type = 'pdf'
                  subtype = None
                  if 'Male' in link.text:
                    subtype = 'male'
                  elif 'Female' in link.text:
                    subtype = 'female'
                  elif 'Vocal' in link.text:
                    subtype = 'music-vocal'
                  elif 'Accompaniment' in link.text:
                    subtype = 'music-accompaniment'
                  asset_id = None
                  if 'assets.churchofjesuschrist.org' in link.get('href'):
                    asset_id = link.get('href').split['/'][-2]
                  chapter_media.append({
                    'type': media_type,
                    'subtype': subtype,
                    'url': link.get('href').split('?')[0].split('#')[0],
                    'id': asset_id,
                    'thumbUrl': None,
                    'startSeconds': None,
                    'endSeconds': None,
                    'source': 'ChurchofJesusChrist.org',
                  })

            # Simplify HTML markup
            selectors_to_add_newline_after = '.line, .question, br'
            for element in content.select(selectors_to_add_newline_after):
              element.insert_after('\n')
              if element.name != 'br':
                element.insert_after(soup.new_tag('br'))
                element.unwrap()
            if config.INCLUDE_COPYRIGHTED_CONTENT:
              
              # Clean up links
              for element in content.select('a'):
                if (element.parent.get('class') and element.parent.get('class')[0] == 'study-summary') or (element.get('class') and element.get('class')[0] == 'study-note-ref'):
                  if element.get('href') and element.get('href').startswith('/'):
                    element.attrs['href'] = '#' + element.attrs['href'].split('#')[1]
                elif element.get('href') and element.get('href').startswith('/'):
                  element.attrs['href'] = 'https://www.churchofjesuschrist.org' + element.attrs['href']
              
              # Clean up footnotes
              for element in content.select('.study-notes ul, .study-notes li, .study-notes p, .study-notes span'):
                if element.get('class'):
                  element.attrs.pop('class')
                if element.get('data-aid'):
                  element.attrs.pop('data-aid')
                if element.get('data-note-category'):
                  element.attrs.pop('data-note-category')
                if element.get('data-type'):
                  if element.get('data-type') == 'verse':
                    element.attrs['class'] = ['footnotes']
                  element.attrs.pop('data-type')
                if element.name in ['span', 'p']:
                  element.unwrap()
            
            # Clean up book titles with dominant text
            dominant_text = content.select_one('.dominant')
            if dominant_text:
              book_title = dominant_text.parent
              for element in book_title.select('.subordinate'):
                element.unwrap()
              for child in book_title.children:
                if child.name != 'br' and child.string != '\n' and not (isinstance(child, Tag) and child.get('class') and child.get('class')[0] == 'dominant'):
                  if child.string == ' ' and child.previous_sibling and child.previous_sibling.name == 'small':
                    child.previous_sibling.append(' ')
                    child.extract()
                  else:
                    child.wrap(soup.new_tag('small'))
                
            # Remove hard line breaks from titles
            for element in content.select('h1 br, h2 br'):
              element.decompose()
            for element in content.select('h1, h2'):
              for child in element.children:
                if child.string == '\n':
                  child.extract()
            
            # Remove unneeded inline elements
            selectors_to_remove = 'span[data-pointer-type]'
            selectors_to_unwrap = '.deity-name, .para-mark, span.marker, .dominant, .subordinate, .language, .translit, .question, .answer, .line, .selah'
            if not config.INCLUDE_COPYRIGHTED_CONTENT:
              selectors_to_remove += ', sup, .study-summary, .study-intro, .study-notes, article[data-uri="/scriptures/dc-testament/od/2"] p:not(#title_number1)'
              selectors_to_unwrap += ', a'
            for element in content.select(selectors_to_remove):
              element.decompose()
            for element in content.select(selectors_to_unwrap):
              element.unwrap()
            
            # Select paragraphs (block elements and images) to be included
            paragraph_selectors = '.page-break, h1, h2, p' # .page-break is for paragraph metadata (it won't be included as a paragraph in final output)
            if config.INCLUDE_IMAGES:
              paragraph_selectors += ', .body-block img'
            if config.INCLUDE_COPYRIGHTED_CONTENT:
              paragraph_selectors += ', .footnotes'
            paragraphs = content.select(paragraph_selectors)
            
            chapter_name = soup.select_one('[data-testid="readerview-header"] > span').text.strip()
            chapter_abbrev = None
            if metadata_scriptures['languages'][bcp47_lang]['translatedNames'][book_slug]['abbrev']:
              chapter_abbrev = chapter_name.replace(metadata_scriptures['languages'][bcp47_lang]['translatedNames'][book_slug]['name'], metadata_scriptures['languages'][bcp47_lang]['translatedNames'][book_slug]['abbrev'])
            
            if config.OUTPUT_AS_JSON:
              chapter_dict = {
                'name': chapter_name,
                'abbrev': chapter_abbrev,
                'number': chapter_number,
                'churchUri': chapter_uri,
                'paragraphs': [],
                'media': chapter_media,
              }
              if config.SPLIT_JSON_BY_CHAPTER:
                chapters_in_publication_count += 1
                json_content = chapter_dict
              else:
                if book_slug not in json_content:
                  json_content[book_slug] = {}
                json_content[book_slug][chapter_slug] = chapter_dict
            
            if chapters_in_publication_count > 1:
              # If this isn't the first chapter in the file, add a horizontal rule
              if config.OUTPUT_AS_HTML:
                html_content += '\n<hr>\n\n'
              if config.OUTPUT_AS_TXT:
                txt_content += '\n--------------------\n\n'
              if config.OUTPUT_AS_MD:
                md_content += '\n---\n\n'
            
            if config.OUTPUT_AS_CSV or config.OUTPUT_AS_TSV or config.OUTPUT_AS_SQL_MYSQL or config.OUTPUT_AS_SQL_SQLITE:
              all_chapters_dict_list.append({
                'pubKey': publication_key,
                'chPosition': len(all_chapters_dict_list),
                'chSlug': chapter_slug,
                'chName': chapter_name,
                'chAbbrev': chapter_abbrev,
                'chNumber': chapter_number,
                'bookSlug': book_slug,
                'chChurchUri': chapter_uri,
              })
              for media_item in chapter_media:
                all_chapter_media_dict_list.append({
                  'pubKey': publication_key,
                  'chSlug': chapter_slug,
                  'chmType': media_item.get('type'),
                  'chmSubType': media_item.get('subtype'),
                  'chmUrl': media_item.get('url'),
                  'chmThumbUrl': media_item.get('thumbUrl'),
                  'chmStartSeconds': media_item.get('startSeconds'),
                  'chmEndSeconds': media_item.get('endSeconds'),
                  'chmSource': media_item.get('source'),
                  'chmChurchAssetId': media_item.get('id'),
                })
            
            if config.OUTPUT_AS_HTML:
              # Make sure paragraph IDs are unique when there are multiple chapters on a page
              paragraph_id_prefix = chapter_slug + '_'
              prepend_chapter_slug_to_paragraph_ids = True
              if not prepend_chapter_slug_to_paragraph_ids:
                paragraph_id_prefix = ''
            
            # Set the initial page number, if it's not already set (this will be used when processing paragraphs)
            first_page_number_element_in_chapter = soup.select_one('.page-break')
            if first_page_number_element_in_chapter and not previous_page_number:
              previous_page_number = str(int(first_page_number_element_in_chapter.attrs['data-page']) - 1)
            
            # Create formatted output for each paragraph
            for paragraph in paragraphs:
              
              # Skip .page-break elements that have already been decomposed
              try:
                is_valid_element = paragraph.get('class')
              except:
                continue
              
              # Get paragraph page number and remove .page-break elements
              paragraph_page_number = previous_page_number
              if paragraph.get('class') and paragraph.get('class')[0] == 'page-break':
                previous_page_number = paragraph.attrs['data-page']
                continue
              page_break_element = paragraph.select_one('.page-break')
              if page_break_element:
                previous_page_number = page_break_element.attrs['data-page']
                paragraph_page_number += ',' + previous_page_number
                page_break_element.decompose()
              
              church_paragraph_id = paragraph.get('id')
              paragraph_type = get_paragraph_type(paragraph)
              paragraph_id = get_paragraph_id(chapter_slug, paragraph_type)
              paragraph_number = get_paragraph_number(paragraph)
              paragraph_compare_id = f'{chapter_slug}_{paragraph_id}'
              
              if config.OUTPUT_AS_JSON:
                # Add paragraph to chapter dict
                paragraph_content = get_paragraph_content(paragraph, content_type='text', id_prefix=paragraph_id_prefix, id=paragraph_id)
                paragraph_content_html = get_paragraph_content(paragraph, content_type='html', id_prefix=paragraph_id_prefix, id=paragraph_id)
                if paragraph_content or paragraph_content_html:
                  chapter_dict['paragraphs'].append({
                    'type': paragraph_type,
                    'id': paragraph_id,
                    'content': paragraph_content,
                    'contentHtml': paragraph_content_html,
                    'number': paragraph_number.strip() if paragraph_number else None,
                    'pageNumber': paragraph_page_number,
                    'compareId': paragraph_compare_id,
                    'churchId': church_paragraph_id,
                  })
            
              if config.OUTPUT_AS_HTML:
                # Add paragraph to HTML string
                paragraph_content = get_paragraph_content(paragraph, content_type='html', include_number=True, id_prefix=paragraph_id_prefix, id=paragraph_id)
                if paragraph_content:
                  if paragraph_type == 'book-title':
                    paragraph_content = f'\n<h1 id="{book_slug}" class="{paragraph_type}">{paragraph_content}</h1>\n'
                  elif paragraph_type == 'chapter-title':
                    paragraph_content = f'\n<h2 id="{chapter_slug}" class="{paragraph_type}">{paragraph_content}</h2>\n'
                  elif paragraph_type == 'section-title':
                    paragraph_content = f'\n<h3 id="{paragraph_id_prefix}{paragraph_id}" class="{paragraph_type}">{paragraph_content}</h3>\n'
                  elif paragraph_type == 'image':
                    paragraph_content = f'{paragraph_content}\n'
                  elif paragraph_type == 'footnotes':
                    paragraph_content = f'<ul id="{paragraph_id_prefix}{paragraph_id}" class="{paragraph_type}">{paragraph_content}</ul>\n'
                  else:
                    paragraph_content = f'<p id="{paragraph_id_prefix}{paragraph_id}" class="{paragraph_type}">{paragraph_content}</p>\n'
                  html_content += paragraph_content
                
              if config.OUTPUT_AS_MD:
                # Add paragraph to markdown string
                paragraph_content = get_paragraph_content(paragraph, content_type='markdown', include_number=True, id_prefix=paragraph_id_prefix)
                if paragraph_content:
                  if paragraph_type == 'book-title':
                    paragraph_anchor = f'<a name="{book_slug}"></a>'
                    paragraph_content = f'# {paragraph_anchor}{paragraph_content}\n\n'
                  elif paragraph_type == 'chapter-title':
                    paragraph_anchor = f'<a name="{chapter_slug}"></a>'
                    paragraph_content = f'## {paragraph_anchor}{paragraph_content}\n\n'
                  elif paragraph_type == 'section-title':
                    paragraph_anchor = f'<a name="{paragraph_id_prefix}{paragraph_id}"></a>'
                    paragraph_content = f'### {paragraph_anchor}{paragraph_content}\n\n'
                  elif paragraph_type == 'image':
                    paragraph_anchor = f'<a name="{paragraph_id_prefix}{paragraph_id}"></a>'
                    paragraph_content = f'{paragraph_anchor}![]({paragraph_content})\n\n'
                  else:
                    paragraph_anchor = f'<a name="{paragraph_id_prefix}{paragraph_id}"></a>'
                    paragraph_content = f'{paragraph_anchor}{paragraph_content}\n\n'
                  md_content += paragraph_content
            
              if config.OUTPUT_AS_TXT:
                # Add paragraph to text string
                paragraph_content = get_paragraph_content(paragraph, content_type='text', include_number=True)
                if paragraph_content:
                  if paragraph_type == 'chapter-title':
                    paragraph_content = paragraph_content.upper()
                  txt_content += paragraph_content + '\n\n'

              if config.OUTPUT_AS_CSV or config.OUTPUT_AS_TSV or config.OUTPUT_AS_SQL_MYSQL or config.OUTPUT_AS_SQL_SQLITE:
                paragraph_content = get_paragraph_content(paragraph, content_type='text', id=paragraph_id)
                paragraph_content_html = get_paragraph_content(paragraph, content_type='html', id=paragraph_id)
                if paragraph_content or paragraph_content_html:
                  all_paragraphs_dict_list.append({
                    'pubKey': publication_key,
                    'chSlug': chapter_slug,
                    'parPosition': len(all_paragraphs_dict_list),
                    'parType': paragraph_type,
                    'parId': paragraph_id,
                    'parContent': paragraph_content,
                    'parContentHtml': paragraph_content_html,
                    'parNumber': paragraph_number,
                    'parPageNumber': paragraph_page_number,
                    'parCompareId': paragraph_compare_id,
                    'parChurchId': church_paragraph_id,
                  })
            
            if config.OUTPUT_AS_JSON and config.SPLIT_JSON_BY_CHAPTER:
              # Create JSON file for a single chapter
              file_extension = 'json'
              file_path = os.path.join(output_directory, f'{bcp47_lang}-{file_extension}', publication_slug, book_slug, f'{chapter_slug}.{file_extension}')
              os.makedirs(os.path.dirname(file_path), exist_ok=True)
              with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_content, fp=f, indent=(None if config.MINIFY_JSON else config.JSON_INDENT), separators=((',', ':') if config.MINIFY_JSON else (', ', ': ')), ensure_ascii=False, sort_keys=False)
      
      # Print summary of chapter-level files created
      if config.OUTPUT_AS_JSON and config.SPLIT_JSON_BY_CHAPTER:
        sys.stdout.write(f'Created {chapters_in_publication_count} chapter JSON files\n')
      
      # Prepare HTML file by putting content into an HTML template
      def prepareHtmlFile(html_content):
        stylesheet_link = ''
        if config.ADD_CSS_STYLESHEET:
          stylesheet_link = '\n    <link rel="stylesheet" type="text/css" href="../styles.css">'
        indented_html_content = html_content.replace('\n', '\n    ')
        return resources.html_template.format(bcp47_lang, metadata_scriptures['languages'][bcp47_lang]['translatedNames'][publication_slug]['name'], stylesheet_link, indented_html_content)
      
      # Create publication-level output file
      def createPublicationFile(file_extension, content):
        file_path = os.path.join(output_directory, f'{bcp47_lang}-{file_extension}', f'{publication_slug}.{file_extension}')
        sys.stdout.write(f'Creating {os.path.basename(file_path)}\n')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
          if file_extension == 'json':
            json.dump(content, fp=f, indent=(None if config.MINIFY_JSON else config.JSON_INDENT), separators=((',', ':') if config.MINIFY_JSON else (', ', ': ')), ensure_ascii=False, sort_keys=False)
          else:
            f.write(content)
      
      # Create publication-level files in each applicable format
      if config.OUTPUT_AS_JSON and not config.SPLIT_JSON_BY_CHAPTER:
        createPublicationFile('json', json_content)
      if config.OUTPUT_AS_HTML:
        createPublicationFile('html', prepareHtmlFile(html_content))
      if config.OUTPUT_AS_MD:
        createPublicationFile('md', md_content)
      if config.OUTPUT_AS_TXT:
        createPublicationFile('txt', txt_content)

      sys.stdout.write('\n')

  # Create CSV or TSV file from a list of dicts
  def create_csv_from_dicts(file_type, file_name, dict_list):
    file_path = os.path.join(output_directory, f'{bcp47_lang}-{file_type}', file_name)
    sys.stdout.write(f'Creating {os.path.basename(file_path)}\n')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
      content = ''
      delimiter = '\t' if (file_type == 'tsv') else ','
      if dict_list:
        writer = csv.DictWriter(f, fieldnames=dict_list[0].keys(), delimiter=delimiter)
        writer.writeheader()
        writer.writerows(dict_list)
      f.write(content)
  
  if config.OUTPUT_AS_CSV:
    # Create CSV files
    create_csv_from_dicts('csv', 'Publications.csv', all_publications_dict_list)
    create_csv_from_dicts('csv', 'Chapters.csv', all_chapters_dict_list)
    create_csv_from_dicts('csv', 'ChapterMedia.csv', all_chapter_media_dict_list)
    create_csv_from_dicts('csv', 'Paragraphs.csv', all_paragraphs_dict_list)
    sys.stdout.write('\n')
    
  if config.OUTPUT_AS_TSV:
    # Create TSV files
    create_csv_from_dicts('tsv', 'Publications.tsv', all_publications_dict_list)
    create_csv_from_dicts('tsv', 'Chapters.tsv', all_chapters_dict_list)
    create_csv_from_dicts('tsv', 'ChapterMedia.tsv', all_chapter_media_dict_list)
    create_csv_from_dicts('tsv', 'Paragraphs.tsv', all_paragraphs_dict_list)
    sys.stdout.write('\n')
        
  if config.OUTPUT_AS_SQL_MYSQL:
    # Create SQL (MySQL) file
    sql_inserts = ''
    sql_inserts += resources.create_sql_insert_statement('Publication', all_publications_dict_list)
    sql_inserts += resources.create_sql_insert_statement('Chapter', all_chapters_dict_list)
    sql_inserts += resources.create_sql_insert_statement('ChapterMedia', all_chapter_media_dict_list)
    sql_inserts += resources.create_sql_insert_statement('Paragraph', all_paragraphs_dict_list)
    content = resources.sql_mysql_template.format(sql_inserts)
    file_path = os.path.join(output_directory, f'{bcp47_lang}-sql-mysql', 'scriptures.sql')
    sys.stdout.write(f'Creating {os.path.basename(file_path)} (MySQL)\n')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
      f.write(content)
    
  if config.OUTPUT_AS_SQL_SQLITE:
    # Create SQL (SQLite) file
    sql_inserts = ''
    sql_inserts += resources.create_sql_insert_statement('Publication', all_publications_dict_list)
    sql_inserts += resources.create_sql_insert_statement('Chapter', all_chapters_dict_list)
    sql_inserts += resources.create_sql_insert_statement('ChapterMedia', all_chapter_media_dict_list)
    sql_inserts += resources.create_sql_insert_statement('Paragraph', all_paragraphs_dict_list)
    content = resources.sql_sqlite_template.format(sql_inserts)
    file_path = os.path.join(output_directory, f'{bcp47_lang}-sql-sqlite', 'scriptures.sql')
    sys.stdout.write(f'Creating {os.path.basename(file_path)} (SQLite)\n')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
      f.write(content)
    
    sys.stdout.write('\n')
    

def print_warning(message):
  sys.stderr.write('\x1b[1;33m' + message + '\x1b[0m')


# 
# FULL CONTENT TEST CASES
#
# Genesis 1: book title before chapter title; italicized clarity words
# Psalm 119: small-caps "Lord"; section headers throughout chapter; Hebrew characters; Psalm singular in both name and slug
# Matthew 1: publication title above chapter; uppercase "Jesus"
# Philippians 4: non-verse paragraph at end of chapter
# 1 Nephi 1: book title before chapter title; non-verse paragraph (book summary) before chapter title
# 1 Nephi 3: regular chapter; footnote superscript letters (removed by default); footnotes (if INCLUDE_COPYRIGHTED_CONTENT)
# Enos 1: book title before chapter title; single-chapter book
# Alma 17: non-verse paragraph (section summary) before chapter title
# Doctrine and Covenants 1: book title before chapter title; summary with jump links (if INCLUDE_COPYRIGHTED_CONTENT)
# Doctrine and Covenants 77: questions and answers
# Doctrine and Covenants 84: poetry with line breaks
# Official Declaration 1: no verses
# Official Declaration 2: copyrighted content (should be skipped)
# Moses 1: book title before chapter title; subtitle under chapter title
# Abraham facsimile 3: image; subtitle under chapter title; not numbered like other chapters; link to other content
# Joseph Smith—History 1: verses and paragraphs; section breaks; links to other chapters (if INCLUDE_COPYRIGHTED_CONTENT)
# 
# Verify that each of the config parameters is respected
# 


if __name__ == '__main__':
  main()