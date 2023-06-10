# Python standard libraries
import os
import sys
import shutil
import json
import csv
from datetime import datetime
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
VERSION = '1.0'

# URL patterns
languages_url = 'https://www.churchofjesuschrist.org/languages?lang=eng'
study_url = 'https://www.churchofjesuschrist.org/study{0}?lang={1}&mboxDisable=1'
abbreviations_url = 'https://www.churchofjesuschrist.org/study/scriptures/quad/quad/abbreviations?lang={0}&mboxDisable=1'

working_directory = os.path.abspath(os.path.dirname(__file__))
output_directory = os.path.join(working_directory, '_output')

skipped_languages = set()
incomplete_volumes = set()

metadata_availability = {
  'languages': {},
  'volumes': {
    'old-testament': [],
    'new-testament': [],
    'book-of-mormon': [],
    'doctrine-and-covenants': [],
    'pearl-of-great-price': [],
  },
  'books': {},
}
metadata_extras = {
  '_': {
    'bookChapterSeparator': ' ',
    'chapterVerseSeparator': ':',
    'verseRangeSeparator': '–',
    'verseGroupSeparator': ', ',
    'referenceSeparator': '; ',
    'numerals': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
    'singularBookNames': {},
    'namedChapters': {},
  },
}

metadata_slug_to_name = {}
metadata_uri_to_name = {}
metadata_name_to_slug = {
  '_': {}
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
  
  # Gather metadata for each language
  for language in languages:
    time.sleep(config.SECONDS_TO_PAUSE_BETWEEN_REQUESTS)
    gather_metadata_for_language(language)
  
  # Print language metadata warnings
  if skipped_languages:
    sys.stdout.write('Skipped {0} language{1} without scripture data ({2})\n'.format(len(skipped_languages), 's'[:len(skipped_languages)^1], ', '.join(sorted(skipped_languages))))
  if incomplete_volumes:
    sys.stdout.write('{0} volume{1} with missing books ({2})\n'.format(len(incomplete_volumes), 's'[:len(incomplete_volumes)^1], ', '.join(sorted(incomplete_volumes))))
  sys.stdout.write('\n')

  # Create metadata files
  sys.stdout.write('Creating metadata-structure.json\n')
  with open(os.path.join(output_directory, 'metadata-structure.json'), 'w', encoding='utf-8') as f:
    json.dump(metadata_structure, fp=f, indent=config.JSON_INDENT, ensure_ascii=False, sort_keys=False)

  sys.stdout.write('Creating metadata-availability.json\n')
  with open(os.path.join(output_directory, 'metadata-availability.json'), 'w', encoding='utf-8') as f:
    json.dump(metadata_availability, fp=f, indent=config.JSON_INDENT, ensure_ascii=False, sort_keys=False)

  sys.stdout.write('Creating metadata-extras.json\n')
  with open(os.path.join(output_directory, 'metadata-extras.json'), 'w', encoding='utf-8') as f:
    json.dump(metadata_extras, fp=f, indent=config.JSON_INDENT, ensure_ascii=False, sort_keys=False)

  sys.stdout.write('Creating metadata-slug-to-name.json\n')
  with open(os.path.join(output_directory, 'metadata-slug-to-name.json'), 'w', encoding='utf-8') as f:
    json.dump(metadata_slug_to_name, fp=f, indent=config.JSON_INDENT, ensure_ascii=False, sort_keys=True)

  sys.stdout.write('Creating metadata-uri-to-name.json\n')
  with open(os.path.join(output_directory, 'metadata-uri-to-name.json'), 'w', encoding='utf-8') as f:
    json.dump(metadata_uri_to_name, fp=f, indent=config.JSON_INDENT, ensure_ascii=False, sort_keys=True)
  
  sys.stdout.write('Creating metadata-name-to-slug.json\n')
  with open(os.path.join(output_directory, 'metadata-name-to-slug.json'), 'w', encoding='utf-8') as f:
    json.dump(metadata_name_to_slug, fp=f, indent=config.JSON_INDENT, ensure_ascii=False, sort_keys=True)
  
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
        sys.stdout.write('Warning: Language “{0}” is not recognized and will be ignored (most likely it was added to Church content recently). To include this language, add it to the language mappings in resources.py.\n'.format(church_lang))
        continue
      autonym = link.text
      name = link.attrs['title']
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


# Gather metadata for an individual language
def gather_metadata_for_language(language):
  available_uris = []
  bcp47_lang = language['bcp47_lang']
  
  # Fetch the root scriptures page to see what exists in the language
  r = requests.get(study_url.format('/scriptures', language['church_lang']))
  r.encoding = 'utf-8'
  if r and r.status_code == 200:
    sys.stdout.write('Gathering metadata: {0} / {1}\n'.format(language['bcp47_lang'], language['name']))
    
    # Parse the scriptures page
    soup = BeautifulSoup(r.text, 'html.parser')
    available_uris = [a.attrs['href'].split('?')[0].replace('/study/', '/') for a in soup.select('#main a[href]')]

  else:
    # If no scriptures exist, skip the language
    skipped_languages.add(bcp47_lang)
    return
  
  # Add language to metadata_availability dictionary
  metadata_availability['languages'][bcp47_lang] = {
    'old-testament': [],
    'new-testament': [],
    'book-of-mormon': [],
    'doctrine-and-covenants': [],
    'pearl-of-great-price': [],
  }
  all_book_slugs = []
  if '/scriptures/ot' in available_uris:
    book_slugs = list(metadata_structure['old-testament']['books'].keys())
    metadata_availability['languages'][bcp47_lang]['old-testament'] = book_slugs
    metadata_availability['volumes']['old-testament'].append(bcp47_lang)
    all_book_slugs += book_slugs
  if '/scriptures/nt' in available_uris:
    book_slugs = list(metadata_structure['new-testament']['books'].keys())
    metadata_availability['languages'][bcp47_lang]['new-testament'] = book_slugs
    metadata_availability['volumes']['new-testament'].append(bcp47_lang)
    all_book_slugs += book_slugs
  if '/scriptures/bofm' in available_uris:
    book_slugs = list(metadata_structure['book-of-mormon']['books'].keys())
    metadata_availability['languages'][bcp47_lang]['book-of-mormon'] = book_slugs
    metadata_availability['volumes']['book-of-mormon'].append(bcp47_lang)
    all_book_slugs += book_slugs
  if '/scriptures/dc-testament' in available_uris:
    book_slugs = list(metadata_structure['doctrine-and-covenants']['books'].keys())
    metadata_availability['languages'][bcp47_lang]['doctrine-and-covenants'] = book_slugs
    metadata_availability['volumes']['doctrine-and-covenants'].append(bcp47_lang)
    all_book_slugs += book_slugs
  if '/scriptures/pgp' in available_uris:
    book_slugs = list(metadata_structure['pearl-of-great-price']['books'].keys())
    metadata_availability['languages'][bcp47_lang]['pearl-of-great-price'] = book_slugs
    metadata_availability['volumes']['pearl-of-great-price'].append(bcp47_lang)
    all_book_slugs += book_slugs
  for book_slug in all_book_slugs:
    if not book_slug in metadata_availability['books']:
      metadata_availability['books'][book_slug] = []
    metadata_availability['books'][book_slug].append(bcp47_lang)
  
  # Add language to metadata_name_to_slug dictionary
  if bcp47_lang not in metadata_name_to_slug:
    metadata_name_to_slug[bcp47_lang] = {}
  
  # Get metadata extras (localized punctuation and numerals)
  metadata_extras[bcp47_lang] = {}
  if bcp47_lang in ['en', 'ase']:
    # English: Use the default values
    metadata_extras[bcp47_lang] = metadata_extras['_']
  elif bcp47_lang == 'am':
    # Python regex doesn't recognize Amharic numerals correctly, so these values are hard-coded
    metadata_extras[bcp47_lang] = {
      'bookChapterSeparator': ' ',
      'chapterVerseSeparator': '፥',
      'verseRangeSeparator': '–',
      'verseGroupSeparator': '፣ ',
      'referenceSeparator': '፤ ',
      'numerals': None,  # Amharic numerals can't be translated 1 to 1 with English numerals
      'singularBookNames': {},
      'namedChapters': {},
    }
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
          metadata_extras[bcp47_lang]['bookChapterSeparator'] = re.match(r'^[^\s]+(.*?)\d+', verse_range_separator_example).group(1)
          metadata_extras[bcp47_lang]['chapterVerseSeparator'] = re.match(r'^.+?\d+(.+?)\d+', verse_range_separator_example).group(1)
          metadata_extras[bcp47_lang]['verseRangeSeparator'] = re.match(r'^.+?\d+.+?\d+(.+?)\d+', verse_range_separator_example).group(1)
          try:
            metadata_extras[bcp47_lang]['verseGroupSeparator'] = re.match(r'^.+?\d+.+?\d+(.+?)\d+', verse_group_separator_example).group(1)
          except:
            # In Indonesian and possibly other languages, the word order is reversed, so use footnote b instead of footnote c
            verse_group_separator_example = footnotes.select_one('#note1b_p1 a, #note1_b_p1 a').text  # 'D&C 68:25, 28'
            metadata_extras[bcp47_lang]['verseGroupSeparator'] = re.match(r'^.+?\d+.+?\d+(.+?)\d+', verse_group_separator_example).group(1)
          metadata_extras[bcp47_lang]['referenceSeparator'] = reference_separator
        verse_number_spans = soup.select('.verse-number')  # '1 ', '2 ', '3 ', etc.
        if verse_number_spans:
          verse_numbers = [re.match(r'(\d+)', span.text).group(1) for span in verse_number_spans]
          metadata_extras[bcp47_lang]['numerals'] = [verse_numbers[9].replace(verse_numbers[0], '')] + verse_numbers[:9]
    else:
      sys.exit('Error: Unable to connect to {0}'.format(study_url.format(study_uri, language['church_lang'])))

  # Get metadata extras (singular book names: psalm, official-declaration)
  metadata_extras[bcp47_lang]['singularBookNames'] = {}
  
  study_uri = '/manual/come-follow-me-for-individuals-and-families-old-testament-2022/33'
  time.sleep(config.SECONDS_TO_PAUSE_BETWEEN_REQUESTS)
  r = requests.get(study_url.format(study_uri, language['church_lang']))
  r.encoding = 'utf-8'
  if r and r.status_code == 200:
    soup = BeautifulSoup(r.text, 'html.parser')
    psalm_example = soup.select_one(f'#p9 a.scripture-ref[href^="/study/scriptures/ot/ps/2?"]').text  # 'Psalm 2'
    try:
      metadata_extras[bcp47_lang]['singularBookNames']['psalm'] = re.match(r'(.+?)\d+', psalm_example).group(1).strip()
    except:
      # Some languages, like Latvian, put the number first for Psalms (2. psalmā)
      metadata_extras[bcp47_lang]['singularBookNames']['psalm'] = re.match(r'\d+\.*(.+)', psalm_example).group(1).strip()
    
  if '/scriptures/dc-testament' in available_uris:
    study_uri = '/scriptures/dc-testament/od'
    time.sleep(config.SECONDS_TO_PAUSE_BETWEEN_REQUESTS)
    r = requests.get(study_url.format(study_uri, language['church_lang']))
    r.encoding = 'utf-8'
    if r and r.status_code == 200:
      soup = BeautifulSoup(r.text, 'html.parser')
      try:
        official_declaration_example = soup.select_one(f'a.list-tile[href^="/study{study_uri}"] .title').text  # 'Official Declaration 1'
        metadata_extras[bcp47_lang]['singularBookNames']['official-declaration'] = re.match(r'(.+?)(?:\d|Ⅰ|፩|一)+', official_declaration_example).group(1).strip()
      except:
        # Some languages, like Guaraní, don't have Official Declarations translated yet
        pass
  
  # Get metadata extras (named chapters: fac-1, fac-2, fac-3)
  metadata_extras[bcp47_lang]['namedChapters'] = {}
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
        metadata_extras[bcp47_lang]['namedChapters']['fac-1'] = chapter_titles[0].text
        metadata_extras[bcp47_lang]['namedChapters']['fac-2'] = chapter_titles[1].text
        metadata_extras[bcp47_lang]['namedChapters']['fac-3'] = chapter_titles[2].text
  
  # Attempt to get book names and abbreviations from "Abbreviations" content (note: this will be skipped when using test data, because abbreviations are assumed to line up with full list of known books in order, but test data skips books)
  if '/scriptures/study-helps' in available_uris and not config.USE_TEST_DATA:
  
    # Fetch the abbreviations page, if it exists
    time.sleep(config.SECONDS_TO_PAUSE_BETWEEN_REQUESTS)
    r = requests.get(abbreviations_url.format(language['church_lang']))
    r.encoding = 'utf-8'
    if r and r.status_code == 200:
      soup = BeautifulSoup(r.text, 'html.parser')
      rows = soup.select('figure table tr')
      
      # Loop through known scripture structure and the list of abbreviations, and map them to each other
      book_counter = 0
      for v, (volume_slug, volume_data) in enumerate(metadata_structure.items()):
        volume_name = soup.select_one('#figure{0}_title1'.format(v+1)).text.strip()
        volume_uri = volume_data['churchUri']
        
        if volume_slug not in metadata_slug_to_name:
          metadata_slug_to_name[volume_slug] = {}
          metadata_uri_to_name[volume_uri] = {}
        
        if bcp47_lang not in metadata_slug_to_name[volume_slug]:
          # Add volume name to metadata_slug_to_name, metadata_uri_to_name, and metadata_name_to_slug
          metadata_slug_to_name[volume_slug][bcp47_lang] = metadata_uri_to_name[volume_uri][bcp47_lang] = {
            'name': volume_name,
            'abbrev': None,
            'type': 'volume',
          }
          metadata_name_to_slug[bcp47_lang][volume_name] = metadata_name_to_slug['_'][volume_name] = volume_slug
        
        for book_slug, book_data in volume_data['books'].items():
          book_row = rows[book_counter]
          book_name = book_row.select('td')[1].text.strip()
          book_abbreviation = book_row.select('td')[0].text.strip()
          
          if book_slug not in metadata_slug_to_name:
            metadata_slug_to_name[book_slug] = {}
            metadata_uri_to_name[book_data['churchUri']] = {}
          
          if bcp47_lang not in metadata_slug_to_name[book_slug]:
            # Add book name and abbreviation to metadata_slug_to_name, metadata_uri_to_name, and metadata_name_to_slug
            metadata_slug_to_name[book_slug][bcp47_lang] = metadata_uri_to_name[book_data['churchUri']][bcp47_lang] = {
              'name': book_name,
              'abbrev': book_abbreviation,
              'type': 'book',
            }
            metadata_name_to_slug[bcp47_lang][book_name] = metadata_name_to_slug['_'][book_name] = book_slug
            metadata_name_to_slug[bcp47_lang][book_abbreviation] = metadata_name_to_slug['_'][book_abbreviation] = book_slug
          
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
        
        if book_slug not in metadata_slug_to_name:
          metadata_slug_to_name[book_slug] = {}
          metadata_uri_to_name[book_uri] = {}
        
        if bcp47_lang not in metadata_slug_to_name[book_slug]:
          # Add book name and abbreviation to metadata_slug_to_name, metadata_uri_to_name, and metadata_name_to_slug
          metadata_slug_to_name[book_slug][bcp47_lang] = metadata_uri_to_name[book_uri][bcp47_lang] = {
            'name': book_name,
            'abbrev': book_abbreviation,
            'type': 'study-help',
          }
          metadata_name_to_slug[bcp47_lang][book_name] = metadata_name_to_slug['_'][book_name] = book_slug
          metadata_name_to_slug[bcp47_lang][book_abbreviation] = metadata_name_to_slug['_'][book_abbreviation] = book_slug
          
      # If book metadata was successfully gathered from the Abbreviations page, return
      return
  
  # Get book names from the scripture volume table of contents
  for volume_slug, volume_data in metadata_structure.items():
    volume_uri = volume_data['churchUri']
    if volume_uri in available_uris:
      time.sleep(config.SECONDS_TO_PAUSE_BETWEEN_REQUESTS)
      r = requests.get(study_url.format(volume_uri, language['church_lang']))
      r.encoding = 'utf-8'
      if r and r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        table_of_contents = soup.select_one('#content .body')
        volume_name = table_of_contents.select_one('header').text.strip()
        
        if volume_slug not in metadata_slug_to_name:
          metadata_slug_to_name[volume_slug] = {}
          metadata_uri_to_name[volume_uri] = {}
        
        if bcp47_lang not in metadata_slug_to_name[volume_slug]:
          # Add volume name to metadata_slug_to_name, metadata_uri_to_name, and metadata_name_to_slug
          metadata_slug_to_name[volume_slug][bcp47_lang] = metadata_uri_to_name[volume_uri][bcp47_lang] = {
            'name': volume_name,
            'abbrev': None,
            'type': 'volume',
          }
          metadata_name_to_slug[bcp47_lang][volume_name] = metadata_name_to_slug['_'][volume_name] = volume_slug
    
        for book_slug, book_data in volume_data['books'].items():
          
          # Get the first chapter link (from the scripture volume's table of contents) that contains the book URI
          first_chapter_link = table_of_contents.select_one('a.list-tile[href^="/study{0}"]'.format(book_data['churchUri']))
          if not first_chapter_link:
            # If book is missing from the volume (selections, or progressive publishing), skip it
            metadata_availability['languages'][bcp47_lang][volume_slug].remove(book_slug)
            metadata_availability['books'][book_slug].remove(bcp47_lang)
            incomplete_volumes.add('{0}/{1}'.format(bcp47_lang, volume_slug))
            continue
          
          # Get the book name by looking for the preceding title
          previous_title = first_chapter_link.find_previous(class_='title')
          book_name = previous_title.text.strip()
          
          # If the previous element is a list item, the chapter link title is the book title (single-chapter book like Enos)
          if first_chapter_link.parent.find_previous_sibling('li'):
            book_name = first_chapter_link.select_one('.title').text.strip()
        
          if book_slug not in metadata_slug_to_name:
            metadata_slug_to_name[book_slug] = {}
            metadata_uri_to_name[book_data['churchUri']] = {}

          if bcp47_lang not in metadata_slug_to_name[book_slug]:
            # Add book name to metadata_slug_to_name, metadata_uri_to_name, and metadata_name_to_slug
            metadata_slug_to_name[book_slug][bcp47_lang] = metadata_uri_to_name[book_data['churchUri']][bcp47_lang] = {
              'name': book_name,
              'abbrev': None,
              'type': 'book',
            }
            metadata_name_to_slug[bcp47_lang][book_name] = metadata_name_to_slug['_'][book_name] = book_slug
            
  return    


# Scrape full content for a given language
def output_full_content(bcp47_lang):
  all_languages_dict_list = []
  all_volumes_dict_list = []
  all_books_dict_list = []
  all_chapters_dict_list = []
  all_paragraphs_dict_list = []
  
  current_language = [l for l in languages if l['bcp47_lang'] == bcp47_lang][0]
  all_languages_dict_list.append({
    'langBcp47': current_language['bcp47_lang'],
    'langChurchCode': current_language['church_lang'],
    'langAutonym': current_language['autonym'],
  })
  
  # Get the type for a given paragraph
  def get_paragraph_type(paragraph):
    type = 'paragraph'
    if paragraph.name == 'h1':
      type = 'book-title'
    if paragraph.get('id') == 'title_number1':
      type = 'chapter-title'
    if paragraph.name == 'h2':
      type = 'section-title'
    if paragraph.get('id') == 'subtitle1':
      type = 'subtitle'
    if paragraph.get('class') and paragraph.get('class')[0] == 'verse':
      type = 'verse'
    if paragraph.get('class') and paragraph.get('class')[0] == 'study-intro':
      type = 'study-intro'
    if paragraph.get('class') and paragraph.get('class')[0] == 'study-summary':
      type = 'study-summary'
    if paragraph.name == 'img':
      type = 'image'
    if paragraph.name == 'ul':
      type = 'footnotes'
    return type
  
  # Get the number for a given paragraph
  def get_paragraph_number(paragraph):
    number = None
    number_span = paragraph.select_one('.verse-number')
    if number_span:
      number = number_span.text.strip()
    return number
  
  # Get the content for a given paragraph
  def get_paragraph_content(paragraph, simple_tags=False, markdown=False, include_number=False, id_prefix=''):
    content = None
        
    # Image paragraph type
    if get_paragraph_type(paragraph) == 'image':
      image_asset_id = paragraph.get('data-assetid')
      image_filename = (paragraph.get('src') or '').split('/')[-1]
      if image_asset_id and image_filename:
        image_url = 'https://assets.ldscdn.org/{0}/{1}/{2}/{3}'.format(image_asset_id[0:2], image_asset_id[2:4], image_asset_id, image_filename)
        content = image_url
      return content
    
    # Copy the paragraph to avoid modifying the original
    temp_paragraph = copy.copy(paragraph)
    
    # Remove verse number if needed
    number_span = temp_paragraph.select_one('.verse-number')
    if number_span and not include_number:
      number_span.decompose()
    
    if config.INCLUDE_INLINE_ELEMENTS and (simple_tags or markdown):
      # Replace spans with simple style tags
      for element in temp_paragraph.select('.verse-number'):
        element.name = 'b'
        element.attrs.pop('class')
      for element in temp_paragraph.select('.clarity-word'):
        element.name = 'i'
        element.attrs.pop('class')
      for element in temp_paragraph.select('sup'):
        element.decompose()    
    
    if simple_tags:
      # Remove links and footnotes
      for element in temp_paragraph.select('a'):
        element.unwrap()
      if temp_paragraph.get('class') and temp_paragraph.get('class')[0] == 'footnotes':
        return None
    
    if config.INCLUDE_INLINE_ELEMENTS and id_prefix:
      # Add prefix to element IDs if needed
      for element in temp_paragraph.select('[id]'):
        element.attrs['id'] = id_prefix + element.attrs['id']
      for element in temp_paragraph.select('[href^="#"]'):
        element.attrs['href'] = element.attrs['href'].replace('#', f'#{id_prefix}', 1)
    
    if config.INCLUDE_INLINE_ELEMENTS and markdown:
      # Text with markdown inline style elements
      for element in temp_paragraph.select('[id]'):
        element_id = element.get('id')
        element.insert(0, f'<a name="{element_id}"></a>')
      content = MarkdownConverter(escape_underscores=False).convert_soup(temp_paragraph)
    elif config.INCLUDE_INLINE_ELEMENTS:
      # Text with HTML inline style elements
      content = temp_paragraph.decode_contents().strip()
    else:
      # Text without inline style elements
      content = temp_paragraph.text.strip()
    
    return content
  
  # Loop through each volume of scripture
  for volume_slug, volume_data in metadata_structure.items():
    if bcp47_lang in metadata_availability['languages'] and metadata_availability['languages'][bcp47_lang][volume_slug]:
      chapters_in_volume_count = 0
      json_content = {}
      html_content = ''
      md_content = ''
      txt_content = ''
      
      if config.OUTPUT_AS_CSV or config.OUTPUT_AS_TSV or config.OUTPUT_AS_SQL_MYSQL or config.OUTPUT_AS_SQL_SQLITE:
        all_volumes_dict_list.append({
          'volumeSlug': volume_slug,
          'langBcp47': bcp47_lang,
          'volumeName': metadata_slug_to_name[volume_slug][bcp47_lang]['name'],
          'volumeAbbrev': metadata_slug_to_name[volume_slug][bcp47_lang]['abbrev'],
          'volumePosition': len(all_volumes_dict_list),
          'volumeChurchUri': volume_data['churchUri'],
        })
      
      for book_slug, book_data in volume_data['books'].items():
        if book_slug in metadata_slug_to_name and bcp47_lang in metadata_slug_to_name[book_slug]:
          sys.stdout.write('Scraping {0} ({1})\n'.format(metadata_slug_to_name[book_slug][bcp47_lang]['name'], book_slug))
        else:
          continue
        
        if config.OUTPUT_AS_CSV or config.OUTPUT_AS_TSV or config.OUTPUT_AS_SQL_MYSQL or config.OUTPUT_AS_SQL_SQLITE:
          all_books_dict_list.append({
            'bookSlug': book_slug,
            'langBcp47': bcp47_lang,
            'bookName': metadata_slug_to_name[book_slug][bcp47_lang]['name'],
            'bookAbbrev': metadata_slug_to_name[book_slug][bcp47_lang]['abbrev'],
            'bookPosition': len(all_books_dict_list),
            'bookChurchUri': book_data['churchUri'],
            'volumeSlug': volume_slug,
          })
        
        for chapter in (list(range(1, book_data['numberedChapters'] + 1)) + book_data['namedChapters']):
          chapter_number = str(chapter)
          singular_book_slug = resources.mapping_plural_to_singular_book_slug.get(book_slug) or book_slug
          chapter_slug = '{0}-{1}'.format(singular_book_slug, chapter_number)
          chapter_uri = '{0}/{1}'.format(book_data['churchUri'], chapter_number)
      
          # Get chapter content
          time.sleep(config.SECONDS_TO_PAUSE_BETWEEN_REQUESTS)
          r = requests.get(study_url.format(chapter_uri, resources.mapping_bcp47_to_church_lang[bcp47_lang]))
          r.encoding = 'utf-8'
          if r and r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            content = soup.select_one('#content')
            
            if content.select_one('article').attrs['data-uri'] != chapter_uri:
              continue

            # Simplify HTML markup
            selectors_to_add_newline_after = '.line, .question, br'
            for element in content.select(selectors_to_add_newline_after):
              element.insert_after('\n')
              if element.name != 'br':
                element.insert_after(soup.new_tag('br'))
                element.unwrap()
            if not config.INCLUDE_INLINE_ELEMENTS:
              selectors_to_convert_to_uppercase = '.small-caps, .uppercase'
              for element in content.select(selectors_to_convert_to_uppercase):
                element.string = element.text.upper()
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
            if config.INCLUDE_INLINE_ELEMENTS:
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
            selectors_to_remove = '.page-break, span[data-pointer-type]'
            selectors_to_unwrap = '.deity-name, .para-mark, span.marker, .dominant, .subordinate, .language, .translit, .question, .answer, .line, .selah'
            if not config.INCLUDE_COPYRIGHTED_CONTENT:
              selectors_to_remove += ', sup, .study-summary, .study-intro, .study-notes, article[data-uri="/scriptures/dc-testament/od/2"] p:not(#title_number1)'
              selectors_to_unwrap += ', a'
            for element in content.select(selectors_to_remove):
              element.decompose()
            for element in content.select(selectors_to_unwrap):
              element.unwrap()
            
            # Select paragraphs (block elements and images) to be included
            paragraph_selectors = 'h1, h2, p'
            if config.INCLUDE_IMAGES:
              paragraph_selectors += ', .body-block img'
            if config.INCLUDE_COPYRIGHTED_CONTENT:
              paragraph_selectors += ', .footnotes'
            paragraphs = content.select(paragraph_selectors)
            
            chapter_name = soup.select_one('[data-testid="panel-header"] > span').text.strip()
            chapter_abbrev = None
            if metadata_slug_to_name[book_slug][bcp47_lang]['abbrev']:
              chapter_abbrev = chapter_name.replace(metadata_slug_to_name[book_slug][bcp47_lang]['name'], metadata_slug_to_name[book_slug][bcp47_lang]['abbrev'])
            
            if config.OUTPUT_AS_JSON:
              chapter_dict = {
                'name': chapter_name,
                'abbrev': chapter_abbrev,
                'number': chapter_number,
                'churchUri': chapter_uri,
                'paragraphs': [],
              }
              if config.SPLIT_BY_CHAPTER:
                chapters_in_volume_count += 1
                json_content = chapter_dict
              else:
                if book_slug not in json_content:
                  json_content[book_slug] = {}
                json_content[book_slug][chapter_slug] = chapter_dict
            
            if chapters_in_volume_count > 1:
              # If this isn't the first chapter in the file, add a horizontal rule
              if config.OUTPUT_AS_HTML:
                html_content += '\n<hr>\n\n'
              if config.OUTPUT_AS_TXT:
                txt_content += '\n--------------------\n\n'
              if config.OUTPUT_AS_MD:
                md_content += '\n---\n\n'
            
            if config.OUTPUT_AS_CSV or config.OUTPUT_AS_TSV or config.OUTPUT_AS_SQL_MYSQL or config.OUTPUT_AS_SQL_SQLITE:
              all_chapters_dict_list.append({
                'chapterSlug': chapter_slug,
                'langBcp47': bcp47_lang,
                'chapterName': chapter_name,
                'chapterAbbrev': chapter_abbrev,
                'chapterNumber': chapter_number,
                'chapterPosition': len(all_chapters_dict_list),
                'chapterChurchUri': chapter_uri,
                'bookSlug': book_slug,
              })
            
            if config.OUTPUT_AS_HTML:
              # Make sure paragraph IDs are unique when there are multiple chapters on a page
              paragraph_id_prefix = chapter_slug + '_'
              prepend_chapter_slug_to_paragraph_ids = True
              if not prepend_chapter_slug_to_paragraph_ids:
                paragraph_id_prefix = ''
                
            # Create formatted output for each paragraph
            for paragraph in paragraphs:
              
              paragraph_id = paragraph.get('id')
              paragraph_slug = f'{chapter_slug}-{paragraph_id}'
              paragraph_type = get_paragraph_type(paragraph)
              paragraph_number = get_paragraph_number(paragraph)
              
              if config.OUTPUT_AS_JSON:
                # Add paragraph to chapter dict
                paragraph_content = get_paragraph_content(paragraph, include_number=False)
                if paragraph_content:
                  chapter_dict['paragraphs'].append({
                    'slug': paragraph_slug,
                    'type': paragraph_type,
                    'number': paragraph_number.strip() if paragraph_number else None,
                    'content': paragraph_content,
                    'churchId': paragraph_id,
                  })
            
              if config.OUTPUT_AS_HTML:
                # Add paragraph to HTML string
                paragraph_content = get_paragraph_content(paragraph, include_number=True, id_prefix=paragraph_id_prefix)
                if paragraph_content:
                  if paragraph_type == 'book-title':
                    paragraph_content = f'\n<h1 id="{book_slug}" class="{paragraph_type}">{paragraph_content}</h1>\n'
                  elif paragraph_type == 'chapter-title':
                    paragraph_content = f'\n<h2 id="{chapter_slug}" class="{paragraph_type}">{paragraph_content}</h2>\n'
                  elif paragraph_type == 'section-title':
                    paragraph_content = f'\n<h3 id="{paragraph_id_prefix}{paragraph_id}" class="{paragraph_type}">{paragraph_content}</h3>\n'
                  elif paragraph_type == 'image':
                    paragraph_content = f'<img id="{paragraph_id_prefix}{paragraph_id}" src="{paragraph_content}">\n'
                  elif paragraph_type == 'footnotes':
                    paragraph_content = f'<ul id="{paragraph_id_prefix}footnotes" class="{paragraph_type}">{paragraph_content}</ul>\n'
                  else:
                    paragraph_content = f'<p id="{paragraph_id_prefix}{paragraph_id}" class="{paragraph_type}">{paragraph_content}</p>\n'
                  html_content += paragraph_content
                
              if config.OUTPUT_AS_MD:
                # Add paragraph to markdown string
                paragraph_content = get_paragraph_content(paragraph, markdown=True, include_number=True, id_prefix=paragraph_id_prefix)
                if paragraph_content:
                  if paragraph_type == 'book-title':
                    paragraph_anchor = f'<a name="{book_slug}"></a>' if config.INCLUDE_INLINE_ELEMENTS else ''
                    paragraph_content = f'# {paragraph_anchor}{paragraph_content}\n\n'
                  elif paragraph_type == 'chapter-title':
                    paragraph_anchor = f'<a name="{chapter_slug}"></a>' if config.INCLUDE_INLINE_ELEMENTS else ''
                    paragraph_content = f'## {paragraph_anchor}{paragraph_content}\n\n'
                  elif paragraph_type == 'section-title':
                    paragraph_anchor = f'<a name="{paragraph_id_prefix}{paragraph_id}"></a>' if config.INCLUDE_INLINE_ELEMENTS else ''
                    paragraph_content = f'### {paragraph_anchor}{paragraph_content}\n\n'
                  elif paragraph_type == 'image':
                    paragraph_anchor = f'<a name="{paragraph_id_prefix}{paragraph_id}"></a>' if config.INCLUDE_INLINE_ELEMENTS else ''
                    paragraph_content = f'{paragraph_anchor}![]({paragraph_content})\n\n'
                  else:
                    paragraph_anchor = f'<a name="{paragraph_id_prefix}{paragraph_id}"></a>' if config.INCLUDE_INLINE_ELEMENTS else ''
                    paragraph_content = f'{paragraph_anchor}{paragraph_content}\n\n'
                  md_content += paragraph_content
            
              if config.OUTPUT_AS_TXT:
                # Add paragraph to text string
                paragraph_content = get_paragraph_content(paragraph, simple_tags=True, include_number=True)
                if paragraph_content:
                  if paragraph_type == 'chapter-title':
                    paragraph_content = paragraph_content.upper()
                  txt_content += paragraph_content + '\n\n'

              if config.OUTPUT_AS_CSV or config.OUTPUT_AS_TSV or config.OUTPUT_AS_SQL_MYSQL or config.OUTPUT_AS_SQL_SQLITE:
                paragraph_content = get_paragraph_content(paragraph, include_number=False)
                if paragraph_content:
                  all_paragraphs_dict_list.append({
                    'paraSlug': paragraph_slug,
                    'langBcp47': bcp47_lang,
                    'paraType': paragraph_type,
                    'paraNumber': paragraph_number,
                    'paraContent': paragraph_content,
                    'paraPosition': len(all_paragraphs_dict_list),
                    'paraChurchId': paragraph_id,
                    'chapterSlug': chapter_slug,
                  })
            
            if config.OUTPUT_AS_JSON and config.SPLIT_BY_CHAPTER:
              # Create JSON file for a single chapter
              file_extension = 'json'
              file_path = os.path.join(output_directory, f'{bcp47_lang}-{file_extension}', volume_slug, book_slug, f'{chapter_slug}.{file_extension}')
              os.makedirs(os.path.dirname(file_path), exist_ok=True)
              with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_content, fp=f, indent=config.JSON_INDENT, ensure_ascii=False, sort_keys=False)
      
      # Print summary of chapter-level files created
      if config.OUTPUT_AS_JSON and config.SPLIT_BY_CHAPTER:
        sys.stdout.write(f'Created {chapters_in_volume_count} chapter JSON files\n')
      
      # Prepare HTML file by putting content into an HTML template
      def prepareHtmlFile(html_content):
        stylesheet_link = ''
        if config.ADD_CSS_STYLESHEET:
          stylesheet_link = '\n    <link rel="stylesheet" type="text/css" href="../styles.css">'
        indented_html_content = html_content.replace('\n', '\n    ')
        return resources.html_template.format(bcp47_lang, metadata_slug_to_name[volume_slug][bcp47_lang]['name'], stylesheet_link, indented_html_content)
      
      # Create volume-level output file
      def createVolumeFile(file_extension, content):
        file_path = os.path.join(output_directory, f'{bcp47_lang}-{file_extension}', f'{volume_slug}.{file_extension}')
        sys.stdout.write(f'Creating {os.path.basename(file_path)}\n')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
          if file_extension == 'json':
            json.dump(content, fp=f, indent=config.JSON_INDENT, ensure_ascii=False, sort_keys=False)
          else:
            f.write(content)
      
      # Create volume-level files in each applicable format
      if config.OUTPUT_AS_JSON and not config.SPLIT_BY_CHAPTER:
        createVolumeFile('json', json_content)
      if config.OUTPUT_AS_HTML:
        createVolumeFile('html', prepareHtmlFile(html_content))
      if config.OUTPUT_AS_MD:
        createVolumeFile('md', md_content)
      if config.OUTPUT_AS_TXT:
        createVolumeFile('txt', txt_content)

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
    create_csv_from_dicts('csv', 'Languages.csv', all_languages_dict_list)
    create_csv_from_dicts('csv', 'Volumes.csv', all_volumes_dict_list)
    create_csv_from_dicts('csv', 'Books.csv', all_books_dict_list)
    create_csv_from_dicts('csv', 'Chapters.csv', all_chapters_dict_list)
    create_csv_from_dicts('csv', 'Paragraphs.csv', all_paragraphs_dict_list)
    sys.stdout.write('\n')
    
  if config.OUTPUT_AS_TSV:
    # Create TSV files
    create_csv_from_dicts('tsv', 'Languages.tsv', all_languages_dict_list)
    create_csv_from_dicts('tsv', 'Volumes.tsv', all_volumes_dict_list)
    create_csv_from_dicts('tsv', 'Books.tsv', all_books_dict_list)
    create_csv_from_dicts('tsv', 'Chapters.tsv', all_chapters_dict_list)
    create_csv_from_dicts('tsv', 'Paragraphs.tsv', all_paragraphs_dict_list)
    sys.stdout.write('\n')
    
  # Create SQL insert statement for a table
  def create_sql_insert_statement(sql_type, table_name, dict_list):
    statement = ''
    if dict_list:
      field_names = dict_list[0].keys()
      field_names_string = ', '.join(field_names)
      statement += f'INSERT INTO {table_name} ({field_names_string})\nVALUES\n'
      
      num_items = len(dict_list)
      for i, item in enumerate(dict_list):
        line_end_punctuation = '' if (i == num_items - 1) else ','
        field_values_string = ', '.join([(str(value) if isinstance(value, int) else ('NULL' if value is None else f'\'{value}\'')) for value in item.values()])
        statement += f'  ({field_values_string}){line_end_punctuation}\n'
        
      if sql_type == 'mysql':
        statement += 'ON DUPLICATE KEY UPDATE\n'
      elif sql_type == 'sqlite':
        primary_key = re.match(r'.+?CREATE TABLE IF NOT EXISTS {0}.+?PRIMARY KEY.*?\((.+?)\)'.format(table_name), resources.sql_sqlite_template, re.DOTALL).group(1)
        statement += f'ON CONFLICT ({primary_key}) DO UPDATE\nSET\n'
        
      num_fields = len(field_names)
      for f, field in enumerate(field_names):
        line_end_punctuation = ';' if (f == num_fields - 1) else ','
        if sql_type == 'mysql':
          statement += f'  {field} = VALUES({field}){line_end_punctuation}\n'
        elif sql_type == 'sqlite':
          statement += f'  {field} = excluded.{field}{line_end_punctuation}\n'
          
      statement += '\n'
    return statement
    
  if config.OUTPUT_AS_SQL_MYSQL:
    # Create SQL (MySQL) file
    sql_inserts = ''
    sql_inserts += create_sql_insert_statement('mysql', 'Language', all_languages_dict_list)
    sql_inserts += create_sql_insert_statement('mysql', 'Volume', all_volumes_dict_list)
    sql_inserts += create_sql_insert_statement('mysql', 'Book', all_books_dict_list)
    sql_inserts += create_sql_insert_statement('mysql', 'Chapter', all_chapters_dict_list)
    sql_inserts += create_sql_insert_statement('mysql', 'Paragraph', all_paragraphs_dict_list)
    content = resources.sql_mysql_template.format(sql_inserts)
    file_path = os.path.join(output_directory, f'{bcp47_lang}-sql-mysql', 'scriptures.sql')
    sys.stdout.write(f'Creating {os.path.basename(file_path)} (MySQL)\n')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
      f.write(content)
    
  if config.OUTPUT_AS_SQL_SQLITE:
    # Create SQL (SQLite) file
    sql_inserts = ''
    sql_inserts += create_sql_insert_statement('sqlite', 'Language', all_languages_dict_list)
    sql_inserts += create_sql_insert_statement('sqlite', 'Volume', all_volumes_dict_list)
    sql_inserts += create_sql_insert_statement('sqlite', 'Book', all_books_dict_list)
    sql_inserts += create_sql_insert_statement('sqlite', 'Chapter', all_chapters_dict_list)
    sql_inserts += create_sql_insert_statement('sqlite', 'Paragraph', all_paragraphs_dict_list)
    content = resources.sql_sqlite_template.format(sql_inserts)
    file_path = os.path.join(output_directory, f'{bcp47_lang}-sql-sqlite', 'scriptures.sql')
    sys.stdout.write(f'Creating {os.path.basename(file_path)} (SQLite)\n')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
      f.write(content)
    
    sys.stdout.write('\n')
    

# 
# FULL CONTENT TEST CASES
#
# Genesis 1: book title before chapter title; italicized clarity words
# Psalm 119: small-caps "Lord"; section headers throughout chapter; Hebrew characters
# Matthew 1: volume title above chapter; uppercase "Jesus"
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