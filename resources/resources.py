import os
import re
from unicodedata import normalize


# MAPPINGS

# A few book slugs need to be converted to singular when being used as part of a chapter slug
mapping_book_to_singular_slug = {
  'psalms': 'psalm',
  'sections': 'section',
  'official-declarations': 'official-declaration',
  'facsimiles': 'facsimile',
  'jst-psalms': 'jst-psalm',
}

# Church content uses three-letter codes that are based on ISO 639-3 (but not fully compliant). This dictionary provides a mapping from Church language codes to industry-standard BCP 47 language tags.
mapping_church_lang_to_bcp47 = { 'afr': 'af', 'alb': 'sq', 'amh': 'am', 'amu': 'amu', 'apw': 'apw', 'ara': 'ar', 'ase': 'ase', 'asf': 'asf', 'awa': 'awa', 'aym': 'ay', 'bam': 'bm', 'bel': 'be', 'bem': 'bem', 'ben': 'bn', 'bfi': 'bfi', 'bik': 'bik', 'bis': 'bi', 'bla': 'bla', 'bos': 'bs', 'bul': 'bg', 'cag': 'cag', 'cak': 'cak', 'cat': 'ca', 'cco': 'cco', 'ceb': 'ceb', 'ces': 'cs', 'cha': 'ch', 'chk': 'chk', 'chr': 'chr', 'ckw': 'ckw', 'cmn': 'cmn', 'cmn-Latn': 'cmn-Latn', 'cuk': 'cuk', 'cym': 'cy', 'dan': 'da', 'deu': 'de', 'efi': 'efi', 'ell': 'el', 'eng': 'en', 'ept': 'pt-PT', 'esp': 'es-ES', 'est': 'et', 'eus': 'eu', 'fat': 'fat', 'fij': 'fj', 'fin': 'fi', 'fon': 'fon', 'fra': 'fr', 'frp': 'fr-PF', 'gil': 'gil', 'gla': 'gd', 'gle': 'ga', 'grn': 'gn', 'guz': 'guz', 'hat': 'ht', 'haw': 'haw', 'heb': 'he', 'hif': 'hif', 'hil': 'hil', 'hin': 'hi', 'hmn': 'hmn', 'hmo': 'ho', 'hrv': 'hr', 'hun': 'hu', 'hwc': 'hwc', 'hye': 'hy', 'hyw': 'hyw', 'iba': 'iba', 'ibo': 'ig', 'ilo': 'ilo', 'ind': 'id', 'isl': 'is', 'ita': 'it', 'jac': 'jac', 'jav': 'jv', 'jpn': 'ja', 'kam': 'kam', 'kan': 'kn', 'kat': 'ka', 'kaz': 'kk', 'kek': 'kek', 'khm': 'km', 'kin': 'rw', 'kon': 'kg', 'kor': 'ko', 'kos': 'kos', 'kpe': 'kpe', 'ksw': 'ksw', 'kur': 'ku', 'lao': 'lo', 'lat': 'la', 'lav': 'lv', 'lin': 'ln', 'lit': 'lt', 'lua': 'lua', 'luo': 'luo', 'mah': 'mh', 'mal': 'ml', 'mam': 'mam', 'mar': 'mr', 'meu': 'meu', 'mfe': 'mfe', 'mis': 'mis', 'mkd': 'mk', 'mlg': 'mg', 'mlt': 'mt', 'mnk': 'mnk', 'mon': 'mn', 'mos': 'mos', 'mri': 'mi', 'msa': 'ms', 'mul': 'mul', 'mvc': 'mvc', 'mya': 'my', 'nav': 'nv', 'nbl': 'nr', 'nds': 'nds', 'nep': 'ne', 'ngu': 'ngu', 'niu': 'niu', 'nld': 'nl', 'nor': 'no', 'nso': 'nso', 'nya': 'ny', 'ori': 'or', 'orm': 'om', 'pag': 'pag', 'pam': 'pam', 'pan': 'pa', 'pap': 'pap', 'pau': 'pau', 'pes': 'pes', 'pol': 'pl', 'pon': 'pon', 'por': 'pt', 'ppl': 'ppl', 'pus': 'ps', 'quc': 'quc', 'que': 'qu', 'quh': 'quh', 'quz': 'quz', 'qvi': 'qvi', 'rar': 'rar', 'ron': 'ro', 'rtm': 'rtm', 'rus': 'ru', 'sin': 'si', 'slk': 'sk', 'slv': 'sl', 'smo': 'sm', 'sna': 'sn', 'som': 'so', 'sot': 'st', 'spa': 'es', 'srb': 'srb', 'srp': 'sr', 'ssw': 'ss', 'sto': 'sto', 'swa': 'sw', 'swe': 'sv', 'tah': 'ty', 'tam': 'ta', 'tel': 'te', 'tgl': 'tl', 'tha': 'th', 'ton': 'to', 'tpi': 'tpi', 'tsn': 'tn', 'tur': 'tr', 'tvl': 'tvl', 'twi': 'tw', 'tzj': 'tzj', 'tzo': 'tzo', 'ukr': 'uk', 'und': 'und', 'urd': 'ur', 'usp': 'usp', 'uzb': 'uz', 'vie': 'vi', 'war': 'war', 'wol': 'wo', 'xho': 'xh', 'yap': 'yap', 'yor': 'yo', 'yua': 'yua', 'yue': 'yue-Hant', 'yue-Latn': 'yue-Latn', 'zdj': 'zdj', 'zho': 'cmn-Hant', 'zhs': 'cmn-Hans', 'zul': 'zu', 'zxx': 'zxx' }

# Mapping from BCP 47 language tags to Church language codes
mapping_bcp47_to_church_lang = { 'af': 'afr', 'am': 'amh', 'amu': 'amu', 'apw': 'apw', 'ar': 'ara', 'ase': 'ase', 'asf': 'asf', 'awa': 'awa', 'ay': 'aym', 'be': 'bel', 'bem': 'bem', 'bfi': 'bfi', 'bg': 'bul', 'bi': 'bis', 'bik': 'bik', 'bla': 'bla', 'bm': 'bam', 'bn': 'ben', 'bs': 'bos', 'ca': 'cat', 'cag': 'cag', 'cak': 'cak', 'cco': 'cco', 'ceb': 'ceb', 'ch': 'cha', 'chk': 'chk', 'chr': 'chr', 'ckw': 'ckw', 'cmn-Hans': 'zhs', 'cmn-Hant': 'zho', 'cmn': 'cmn', 'cmn-Latn': 'cmn-Latn', 'cs': 'ces', 'cuk': 'cuk', 'cy': 'cym', 'da': 'dan', 'de': 'deu', 'efi': 'efi', 'el': 'ell', 'en': 'eng', 'es-ES': 'esp', 'es': 'spa', 'et': 'est', 'eu': 'eus', 'fat': 'fat', 'fi': 'fin', 'fj': 'fij', 'fon': 'fon', 'fr-PF': 'frp', 'fr': 'fra', 'ga': 'gle', 'gd': 'gla', 'gil': 'gil', 'gn': 'grn', 'guz': 'guz', 'haw': 'haw', 'he': 'heb', 'hi': 'hin', 'hif': 'hif', 'hil': 'hil', 'hmn': 'hmn', 'ho': 'hmo', 'hr': 'hrv', 'ht': 'hat', 'hu': 'hun', 'hwc': 'hwc', 'hy': 'hye', 'hyw': 'hyw', 'iba': 'iba', 'id': 'ind', 'ig': 'ibo', 'ilo': 'ilo', 'is': 'isl', 'it': 'ita', 'ja': 'jpn', 'jac': 'jac', 'jv': 'jav', 'ka': 'kat', 'kam': 'kam', 'kek': 'kek', 'kg': 'kon', 'kk': 'kaz', 'km': 'khm', 'kn': 'kan', 'ko': 'kor', 'kos': 'kos', 'kpe': 'kpe', 'ksw': 'ksw', 'ku': 'kur', 'la': 'lat', 'ln': 'lin', 'lo': 'lao', 'lt': 'lit', 'lua': 'lua', 'luo': 'luo', 'lv': 'lav', 'mam': 'mam', 'meu': 'meu', 'mfe': 'mfe', 'mg': 'mlg', 'mh': 'mah', 'mi': 'mri', 'mis': 'mis', 'mk': 'mkd', 'ml': 'mal', 'mn': 'mon', 'mnk': 'mnk', 'mos': 'mos', 'mr': 'mar', 'ms': 'msa', 'mt': 'mlt', 'mul': 'mul', 'mvc': 'mvc', 'my': 'mya', 'nds': 'nds', 'ne': 'nep', 'ngu': 'ngu', 'niu': 'niu', 'nl': 'nld', 'no': 'nor', 'nr': 'nbl', 'nso': 'nso', 'nv': 'nav', 'ny': 'nya', 'om': 'orm', 'or': 'ori', 'pa': 'pan', 'pag': 'pag', 'pam': 'pam', 'pap': 'pap', 'pau': 'pau', 'pes': 'pes', 'pl': 'pol', 'pon': 'pon', 'ppl': 'ppl', 'ps': 'pus', 'pt-PT': 'ept', 'pt': 'por', 'qu': 'que', 'quc': 'quc', 'quh': 'quh', 'quz': 'quz', 'qvi': 'qvi', 'rar': 'rar', 'ro': 'ron', 'rtm': 'rtm', 'ru': 'rus', 'rw': 'kin', 'si': 'sin', 'sk': 'slk', 'sl': 'slv', 'sm': 'smo', 'sn': 'sna', 'so': 'som', 'sq': 'alb', 'sr': 'srp', 'srb': 'srb', 'ss': 'ssw', 'st': 'sot', 'sto': 'sto', 'sv': 'swe', 'sw': 'swa', 'ta': 'tam', 'te': 'tel', 'th': 'tha', 'tl': 'tgl', 'tn': 'tsn', 'to': 'ton', 'tpi': 'tpi', 'tr': 'tur', 'tvl': 'tvl', 'tw': 'twi', 'ty': 'tah', 'tzj': 'tzj', 'tzo': 'tzo', 'uk': 'ukr', 'und': 'und', 'ur': 'urd', 'usp': 'usp', 'uz': 'uzb', 'vi': 'vie', 'war': 'war', 'wo': 'wol', 'xh': 'xho', 'yap': 'yap', 'yo': 'yor', 'yua': 'yua', 'yue-Hant': 'yue', 'yue-Latn': 'yue-Latn', 'zdj': 'zdj', 'zu': 'zul', 'zxx': 'zxx' }

# Mapping from paragraph type slug to paragraph type abbreviation
mapping_paragraph_type_to_paragraph_type_abbrev = {
  'paragraph': 'p',
  'book-title': 'bt',
  'book-subtitle': 'bs',
  'chapter-title': 'ct',
  'chapter-subtitle': 'cs',
  'section-title': 'st',
  'verse': 'v',
  'image': 'img',
  'study-section-title': 'sst',
  'study-paragraph': 'sp',
  'study-footnotes': 'sft',
}


# METADATA

# Information about Bible versions from ChurchofJesusChrist.org
bible_version_info = {
  'en': {
    'old-testament': {
      'versionKey': 'kjv',
      'versionAbbrev': 'KJV',
      'versionName': 'King James Version',
      'editionYear': '2013',
      'firstEditionYear': '1611',
      'copyrightStatement': '© 2013 by Intellectual Reserve, Inc.',
      'copyrightOwner': 'iri',
    },
    'new-testament': {
      'versionKey': 'kjv',
      'versionAbbrev': 'KJV',
      'versionName': 'King James Version',
      'editionYear': '2013',
      'firstEditionYear': '1611',
      'copyrightStatement': '© 2013 by Intellectual Reserve, Inc.',
      'copyrightOwner': 'iri',
    },
  },
  'es': {
    'old-testament': {
      'versionKey': 'rv2015',
      'versionAbbrev': 'RV 2015',
      'versionName': 'Reina–Valera 2015',
      'editionYear': '2015',
      'firstEditionYear': '1569',
      'copyrightStatement': '© 2013 by Intellectual Reserve, Inc.',
      'copyrightOwner': 'iri',
    },
    'new-testament': {
      'versionKey': 'rv2015',
      'versionAbbrev': 'RV 2015',
      'versionName': 'Reina–Valera 2015',
      'editionYear': '2015',
      'firstEditionYear': '1569',
      'copyrightStatement': '© 2013 by Intellectual Reserve, Inc.',
      'copyrightOwner': 'iri',
    },
  },
  'fr': {
    'old-testament': {
      'versionKey': 'ls1910',
      'versionAbbrev': 'LS 1910',
      'versionName': 'Louis Segond 1910',
      'editionYear': '1910',
      'firstEditionYear': '1910',
      'copyrightStatement': 'Public domain',
      'copyrightOwner': 'N/A',
    },
    'new-testament': {
      'versionKey': 'ls1910',
      'versionAbbrev': 'LS 1910',
      'versionName': 'Louis Segond 1910',
      'editionYear': '1910',
      'firstEditionYear': '1910',
      'copyrightStatement': 'Public domain',
      'copyrightOwner': 'N/A',
    },
  },
  'pt': {
    'old-testament': {
      'versionKey': 'alm2015',
      'versionAbbrev': 'ALM 2015',
      'versionName': 'Almeida 2015',
      'editionYear': '2015',
      'firstEditionYear': '1753',
      'copyrightStatement': '© 2013 by Intellectual Reserve, Inc.',
      'copyrightOwner': 'iri',
    },
    'new-testament': {
      'versionKey': 'alm2015',
      'versionAbbrev': 'ALM 2015',
      'versionName': 'Almeida 2015',
      'editionYear': '2015',
      'firstEditionYear': '1681',
      'copyrightStatement': '© 2013 by Intellectual Reserve, Inc.',
      'copyrightOwner': 'iri',
    },
  },
}

# First edition years for the Book of Mormon, Doctrine and Covenants, Pearl of Great Price, and JST Appendix
first_edition_years = {
  'en': {
    'book-of-mormon': '1830',
    'doctrine-and-covenants': '1835',
    'pearl-of-great-price': '1851',
    'jst-appendix': '1979',
  },
  'es': {
    'book-of-mormon': '1886',
    'doctrine-and-covenants': '1948',
    'pearl-of-great-price': '1948',
    'jst-appendix': '1993',
  },
  'fr': {
    'book-of-mormon': '1852',
    'doctrine-and-covenants': '1958',
    'pearl-of-great-price': '1958',
    'jst-appendix': '1988',
  },
  'pt': {
    'book-of-mormon': '1939',
    'doctrine-and-covenants': '1950',
    'pearl-of-great-price': '1950',
    'jst-appendix': '1998',
  },
}


# Data for publications, books, and chapters
# Note: In some Bible translations, Esther, Daniel, Joel, and/or Malachi have different numbers of chapters. Also, versification and divisions of verses between chapters may vary. Bible metadata below is based on the King James Version. More info:
# https://catholic-resources.org/Bible/OT-Statistics-Compared.htm
# https://catholic-resources.org/Bible/NT-Statistics-Greek.htm
metadata_structure = {
  'old-testament': {
    'name': 'Old Testament',
    'abbrev': 'ot',
    'churchUri': '/scriptures/ot',
    'books': {
      'genesis': {
        'churchUri': '/scriptures/ot/gen',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50],
        'bookGroup': 'Books of the Law',
      },
      'exodus': {
        'churchUri': '/scriptures/ot/ex',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40],
        'bookGroup': 'Books of the Law',
      },
      'leviticus': {
        'churchUri': '/scriptures/ot/lev',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],
        'bookGroup': 'Books of the Law',
      },
      'numbers': {
        'churchUri': '/scriptures/ot/num',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],
        'bookGroup': 'Books of the Law',
      },
      'deuteronomy': {
        'churchUri': '/scriptures/ot/deut',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34],
        'bookGroup': 'Books of the Law',
      },
      'joshua': {
        'churchUri': '/scriptures/ot/josh',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
        'bookGroup': 'Books of History',
      },
      'judges': {
        'churchUri': '/scriptures/ot/judg',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21],
        'bookGroup': 'Books of History',
      },
      'ruth': {
        'churchUri': '/scriptures/ot/ruth',
        'churchChapters': [1, 2, 3, 4],
        'bookGroup': 'Books of History',
      },
      '1-samuel': {
        'churchUri': '/scriptures/ot/1-sam',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31],
        'bookGroup': 'Books of History',
      },
      '2-samuel': {
        'churchUri': '/scriptures/ot/2-sam',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
        'bookGroup': 'Books of History',
      },
      '1-kings': {
        'churchUri': '/scriptures/ot/1-kgs',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
        'bookGroup': 'Books of History',
      },
      '2-kings': {
        'churchUri': '/scriptures/ot/2-kgs',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
        'bookGroup': 'Books of History',
      },
      '1-chronicles': {
        'churchUri': '/scriptures/ot/1-chr',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
        'bookGroup': 'Books of History',
      },
      '2-chronicles': {
        'churchUri': '/scriptures/ot/2-chr',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],
        'bookGroup': 'Books of History',
      },
      'ezra': {
        'churchUri': '/scriptures/ot/ezra',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'bookGroup': 'Books of History',
      },
      'nehemiah': {
        'churchUri': '/scriptures/ot/neh',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
        'bookGroup': 'Books of History',
      },
      'esther': {
        'churchUri': '/scriptures/ot/esth',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'bookGroup': 'Books of History',
      },
      'job': {
        'churchUri': '/scriptures/ot/job',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42],
        'bookGroup': 'Wisdom and Poetry',
      },
      'psalms': {
        'churchUri': '/scriptures/ot/ps',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150],
        'bookGroup': 'Wisdom and Poetry',
      },
      'proverbs': {
        'churchUri': '/scriptures/ot/prov',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31],
        'bookGroup': 'Wisdom and Poetry',
      },
      'ecclesiastes': {
        'churchUri': '/scriptures/ot/eccl',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        'bookGroup': 'Wisdom and Poetry',
      },
      'song-of-solomon': {
        'churchUri': '/scriptures/ot/song',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8],
        'bookGroup': 'Wisdom and Poetry',
      },
      'isaiah': {
        'churchUri': '/scriptures/ot/isa',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66],
        'bookGroup': 'Books of the Prophets',
      },
      'jeremiah': {
        'churchUri': '/scriptures/ot/jer',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52],
        'bookGroup': 'Books of the Prophets',
      },
      'lamentations': {
        'churchUri': '/scriptures/ot/lam',
        'churchChapters': [1, 2, 3, 4, 5],
        'bookGroup': 'Books of the Prophets',
      },
      'ezekiel': {
        'churchUri': '/scriptures/ot/ezek',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48],
        'bookGroup': 'Books of the Prophets',
      },
      'daniel': {
        'churchUri': '/scriptures/ot/dan',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        'bookGroup': 'Books of the Prophets',
      },
      'hosea': {
        'churchUri': '/scriptures/ot/hosea',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
        'bookGroup': 'Books of the Prophets',
      },
      'joel': {
        'churchUri': '/scriptures/ot/joel',
        'churchChapters': [1, 2, 3],
        'bookGroup': 'Books of the Prophets',
      },
      'amos': {
        'churchUri': '/scriptures/ot/amos',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9],
        'bookGroup': 'Books of the Prophets',
      },
      'obadiah': {
        'churchUri': '/scriptures/ot/obad',
        'churchChapters': [1],
        'bookGroup': 'Books of the Prophets',
      },
      'jonah': {
        'churchUri': '/scriptures/ot/jonah',
        'churchChapters': [1, 2, 3, 4],
        'bookGroup': 'Books of the Prophets',
      },
      'micah': {
        'churchUri': '/scriptures/ot/micah',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7],
        'bookGroup': 'Books of the Prophets',
      },
      'nahum': {
        'churchUri': '/scriptures/ot/nahum',
        'churchChapters': [1, 2, 3],
        'bookGroup': 'Books of the Prophets',
      },
      'habakkuk': {
        'churchUri': '/scriptures/ot/hab',
        'churchChapters': [1, 2, 3],
        'bookGroup': 'Books of the Prophets',
      },
      'zephaniah': {
        'churchUri': '/scriptures/ot/zeph',
        'churchChapters': [1, 2, 3],
        'bookGroup': 'Books of the Prophets',
      },
      'haggai': {
        'churchUri': '/scriptures/ot/hag',
        'churchChapters': [1, 2],
        'bookGroup': 'Books of the Prophets',
      },
      'zechariah': {
        'churchUri': '/scriptures/ot/zech',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
        'bookGroup': 'Books of the Prophets',
      },
      'malachi': {
        'churchUri': '/scriptures/ot/mal',
        'churchChapters': [1, 2, 3, 4],
        'bookGroup': 'Books of the Prophets',
      },
      'tobit': {
        'churchUri': None,
        'churchChapters': [],
        'bookGroup': 'Deuterocanonical Books',
      },
      'judith': {
        'churchUri': None,
        'churchChapters': [],
        'bookGroup': 'Deuterocanonical Books',
      },
      '1-maccabees': {
        'churchUri': None,
        'churchChapters': [],
        'bookGroup': 'Deuterocanonical Books',
      },
      '2-maccabees': {
        'churchUri': None,
        'churchChapters': [],
        'bookGroup': 'Deuterocanonical Books',
      },
      'wisdom-of-solomon': {
        'churchUri': None,
        'churchChapters': [],
        'bookGroup': 'Deuterocanonical Books',
      },
      'sirach': {
        'churchUri': None,
        'churchChapters': [],
        'bookGroup': 'Deuterocanonical Books',
      },
      'baruch': {
        'churchUri': None,
        'churchChapters': [],
        'bookGroup': 'Deuterocanonical Books',
      },
    },
  },
  'new-testament': {
    'name': 'New Testament',
    'abbrev': 'nt',
    'churchUri': '/scriptures/nt',
    'books': {
      'matthew': {
        'churchUri': '/scriptures/nt/matt',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28],
        'bookGroup': 'The Gospels',
      },
      'mark': {
        'churchUri': '/scriptures/nt/mark',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
        'bookGroup': 'The Gospels',
      },
      'luke': {
        'churchUri': '/scriptures/nt/luke',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
        'bookGroup': 'The Gospels',
      },
      'john': {
        'churchUri': '/scriptures/nt/john',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21],
        'bookGroup': 'The Gospels',
      },
      'acts': {
        'churchUri': '/scriptures/nt/acts',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28],
        'bookGroup': 'Acts of the Apostles',
      },
      'romans': {
        'churchUri': '/scriptures/nt/rom',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
        'bookGroup': 'Epistles',
      },
      '1-corinthians': {
        'churchUri': '/scriptures/nt/1-cor',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
        'bookGroup': 'Epistles',
      },
      '2-corinthians': {
        'churchUri': '/scriptures/nt/2-cor',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
        'bookGroup': 'Epistles',
      },
      'galatians': {
        'churchUri': '/scriptures/nt/gal',
        'churchChapters': [1, 2, 3, 4, 5, 6],
        'bookGroup': 'Epistles',
      },
      'ephesians': {
        'churchUri': '/scriptures/nt/eph',
        'churchChapters': [1, 2, 3, 4, 5, 6],
        'bookGroup': 'Epistles',
      },
      'philippians': {
        'churchUri': '/scriptures/nt/philip',
        'churchChapters': [1, 2, 3, 4],
        'bookGroup': 'Epistles',
      },
      'colossians': {
        'churchUri': '/scriptures/nt/col',
        'churchChapters': [1, 2, 3, 4],
        'bookGroup': 'Epistles',
      },
      '1-thessalonians': {
        'churchUri': '/scriptures/nt/1-thes',
        'churchChapters': [1, 2, 3, 4, 5],
        'bookGroup': 'Epistles',
      },
      '2-thessalonians': {
        'churchUri': '/scriptures/nt/2-thes',
        'churchChapters': [1, 2, 3],
        'bookGroup': 'Epistles',
      },
      '1-timothy': {
        'churchUri': '/scriptures/nt/1-tim',
        'churchChapters': [1, 2, 3, 4, 5, 6],
        'bookGroup': 'Epistles',
      },
      '2-timothy': {
        'churchUri': '/scriptures/nt/2-tim',
        'churchChapters': [1, 2, 3, 4],
        'bookGroup': 'Epistles',
      },
      'titus': {
        'churchUri': '/scriptures/nt/titus',
        'churchChapters': [1, 2, 3],
        'bookGroup': 'Epistles',
      },
      'philemon': {
        'churchUri': '/scriptures/nt/philem',
        'churchChapters': [1],
        'bookGroup': 'Epistles',
      },
      'hebrews': {
        'churchUri': '/scriptures/nt/heb',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
        'bookGroup': 'Epistles',
      },
      'james': {
        'churchUri': '/scriptures/nt/james',
        'churchChapters': [1, 2, 3, 4, 5],
        'bookGroup': 'Epistles',
      },
      '1-peter': {
        'churchUri': '/scriptures/nt/1-pet',
        'churchChapters': [1, 2, 3, 4, 5],
        'bookGroup': 'Epistles',
      },
      '2-peter': {
        'churchUri': '/scriptures/nt/2-pet',
        'churchChapters': [1, 2, 3],
        'bookGroup': 'Epistles',
      },
      '1-john': {
        'churchUri': '/scriptures/nt/1-jn',
        'churchChapters': [1, 2, 3, 4, 5],
        'bookGroup': 'Epistles',
      },
      '2-john': {
        'churchUri': '/scriptures/nt/2-jn',
        'churchChapters': [1],
        'bookGroup': 'Epistles',
      },
      '3-john': {
        'churchUri': '/scriptures/nt/3-jn',
        'churchChapters': [1],
        'bookGroup': 'Epistles',
      },
      'jude': {
        'churchUri': '/scriptures/nt/jude',
        'churchChapters': [1],
        'bookGroup': 'Epistles',
      },
      'revelation': {
        'churchUri': '/scriptures/nt/rev',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
        'bookGroup': 'Revelation',
      },
    },
  },
  'book-of-mormon': {
    'name': 'Book of Mormon',
    'abbrev': 'bom',
    'churchUri': '/scriptures/bofm',
    'books': {
      '1-nephi': {
        'churchUri': '/scriptures/bofm/1-ne',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
        'bookGroup': None,
      },
      '2-nephi': {
        'churchUri': '/scriptures/bofm/2-ne',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33],
        'bookGroup': None,
      },
      'jacob': {
        'churchUri': '/scriptures/bofm/jacob',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7],
        'bookGroup': None,
      },
      'enos': {
        'churchUri': '/scriptures/bofm/enos',
        'churchChapters': [1],
        'bookGroup': None,
      },
      'jarom': {
        'churchUri': '/scriptures/bofm/jarom',
        'churchChapters': [1],
        'bookGroup': None,
      },
      'omni': {
        'churchUri': '/scriptures/bofm/omni',
        'churchChapters': [1],
        'bookGroup': None,
      },
      'words-of-mormon': {
        'churchUri': '/scriptures/bofm/w-of-m',
        'churchChapters': [1],
        'bookGroup': None,
      },
      'mosiah': {
        'churchUri': '/scriptures/bofm/mosiah',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
        'bookGroup': None,
      },
      'alma': {
        'churchUri': '/scriptures/bofm/alma',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63],
        'bookGroup': None,
      },
      'helaman': {
        'churchUri': '/scriptures/bofm/hel',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
        'bookGroup': None,
      },
      '3-nephi': {
        'churchUri': '/scriptures/bofm/3-ne',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
        'bookGroup': None,
      },
      '4-nephi': {
        'churchUri': '/scriptures/bofm/4-ne',
        'churchChapters': [1],
        'bookGroup': None,
      },
      'mormon': {
        'churchUri': '/scriptures/bofm/morm',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9],
        'bookGroup': None,
      },
      'ether': {
        'churchUri': '/scriptures/bofm/ether',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        'bookGroup': None,
      },
      'moroni': {
        'churchUri': '/scriptures/bofm/moro',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'bookGroup': None,
      },
    },
  },
  'doctrine-and-covenants': {
    'name': 'Doctrine and Covenants',
    'abbrev': 'dc',
    'churchUri': '/scriptures/dc-testament',
    'books': {
      'sections': {
        'churchUri': '/scriptures/dc-testament/dc',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138],
        'bookGroup': None,
      },
      'official-declarations': {
        'churchUri': '/scriptures/dc-testament/od',
        'churchChapters': [1, 2],
        'bookGroup': None,
      },
    },
  },
  'pearl-of-great-price': {
    'name': 'Pearl of Great Price',
    'abbrev': 'pgp',
    'churchUri': '/scriptures/pgp',
    'books': {
      'moses': {
        'churchUri': '/scriptures/pgp/moses',
        'churchChapters': [1, 2, 3, 4, 5, 6, 7, 8],
        'bookGroup': None,
      },
      'abraham': {
        'churchUri': '/scriptures/pgp/abr',
        'churchChapters': [1, 2, 3, 4, 5, 'fac-1', 'fac-2', 'fac-3'],
        'bookGroup': None,
      },
      'joseph-smith-matthew': {
        'churchUri': '/scriptures/pgp/js-m',
        'churchChapters': [1],
        'bookGroup': None,
      },
      'joseph-smith-history': {
        'churchUri': '/scriptures/pgp/js-h',
        'churchChapters': [1],
        'bookGroup': None,
      },
      'articles-of-faith': {
        'churchUri': '/scriptures/pgp/a-of-f',
        'churchChapters': [1],
        'bookGroup': None,
      },
    },
  },
  'jst-appendix': {
    'name': 'Joseph Smith Translation Appendix',
    'abbrev': 'jst',
    'churchUri': '/scriptures/jst',
    'books': {
      'jst-genesis': {
        'churchUri': '/scriptures/jst/jst-gen',
        'churchChapters': ['1-8', 9, 14, 15, 17, 19, 21, 48, 50],
        'bookGroup': None,
      },
      'jst-exodus': {
        'churchUri': '/scriptures/jst/jst-ex',
        'churchChapters': [4, 18, 22, 32, 33, 34],
        'bookGroup': None,
      },
      'jst-deuteronomy': {
        'churchUri': '/scriptures/jst/jst-deut',
        'churchChapters': [10],
        'bookGroup': None,
      },
      'jst-1-samuel': {
        'churchUri': '/scriptures/jst/jst-1-sam',
        'churchChapters': [16],
        'bookGroup': None,
      },
      'jst-2-samuel': {
        'churchUri': '/scriptures/jst/jst-2-sam',
        'churchChapters': [12],
        'bookGroup': None,
      },
      'jst-1-chronicles': {
        'churchUri': '/scriptures/jst/jst-1-chr',
        'churchChapters': [21],
        'bookGroup': None,
      },
      'jst-2-chronicles': {
        'churchUri': '/scriptures/jst/jst-2-chr',
        'churchChapters': [18],
        'bookGroup': None,
      },
      'jst-psalms': {
        'churchUri': '/scriptures/jst/jst-ps',
        'churchChapters': [11, 14, 24, 109],
        'bookGroup': None,
      },
      'jst-isaiah': {
        'churchUri': '/scriptures/jst/jst-isa',
        'churchChapters': [29, 42],
        'bookGroup': None,
      },
      'jst-jeremiah': {
        'churchUri': '/scriptures/jst/jst-jer',
        'churchChapters': [26],
        'bookGroup': None,
      },
      'jst-amos': {
        'churchUri': '/scriptures/jst/jst-amos',
        'churchChapters': [7],
        'bookGroup': None,
      },
      'jst-matthew': {
        'churchUri': '/scriptures/jst/jst-matt',
        'churchChapters': [3, 4, 5, 6, 7, 9, 11, 12, 13, 16, 17, 18, 19, 21, 23, 26, 27],
        'bookGroup': None,
      },
      'jst-mark': {
        'churchUri': '/scriptures/jst/jst-mark',
        'churchChapters': [2, 3, 7, 8, 9, 12, 14, 16],
        'bookGroup': None,
      },
      'jst-luke': {
        'churchUri': '/scriptures/jst/jst-luke',
        'churchChapters': [1, 2, 3, 6, 9, 11, 12, 14, 16, 17, 18, 21, 23, 24],
        'bookGroup': None,
      },
      'jst-john': {
        'churchUri': '/scriptures/jst/jst-john',
        'churchChapters': [1, 4, 6, 13, 14],
        'bookGroup': None,
      },
      'jst-acts': {
        'churchUri': '/scriptures/jst/jst-acts',
        'churchChapters': [9, 22],
        'bookGroup': None,
      },
      'jst-romans': {
        'churchUri': '/scriptures/jst/jst-rom',
        'churchChapters': [3, 4, 7, 8, 13],
        'bookGroup': None,
      },
      'jst-1-corinthians': {
        'churchUri': '/scriptures/jst/jst-1-cor',
        'churchChapters': [7, 15],
        'bookGroup': None,
      },
      'jst-2-corinthians': {
        'churchUri': '/scriptures/jst/jst-2-cor',
        'churchChapters': [5],
        'bookGroup': None,
      },
      'jst-galatians': {
        'churchUri': '/scriptures/jst/jst-gal',
        'churchChapters': [3],
        'bookGroup': None,
      },
      'jst-ephesians': {
        'churchUri': '/scriptures/jst/jst-eph',
        'churchChapters': [4],
        'bookGroup': None,
      },
      'jst-colossians': {
        'churchUri': '/scriptures/jst/jst-col',
        'churchChapters': [2],
        'bookGroup': None,
      },
      'jst-1-thessalonians': {
        'churchUri': '/scriptures/jst/jst-1-thes',
        'churchChapters': [4],
        'bookGroup': None,
      },
      'jst-2-thessalonians': {
        'churchUri': '/scriptures/jst/jst-2-thes',
        'churchChapters': [2],
        'bookGroup': None,
      },
      'jst-1-timothy': {
        'churchUri': '/scriptures/jst/jst-1-tim',
        'churchChapters': [2, 3, 6],
        'bookGroup': None,
      },
      'jst-hebrews': {
        'churchUri': '/scriptures/jst/jst-heb',
        'churchChapters': [1, 4, 6, 7, 11],
        'bookGroup': None,
      },
      'jst-james': {
        'churchUri': '/scriptures/jst/jst-james',
        'churchChapters': [1, 2],
        'bookGroup': None,
      },
      'jst-1-peter': {
        'churchUri': '/scriptures/jst/jst-1-pet',
        'churchChapters': [3, 4],
        'bookGroup': None,
      },
      'jst-2-peter': {
        'churchUri': '/scriptures/jst/jst-2-pet',
        'churchChapters': [3],
        'bookGroup': None,
      },
      'jst-1-john': {
        'churchUri': '/scriptures/jst/jst-1-jn',
        'churchChapters': [2, 3, 4],
        'bookGroup': None,
      },
      'jst-revelation': {
        'churchUri': '/scriptures/jst/jst-rev',
        'churchChapters': [1, 2, 5, 12, 19],
        'bookGroup': None,
      },
    },
  },
}

# Test data (only a few books and chapters are included, for faster testing)
test_data_structure = {
  'old-testament': {
    'name': 'Old Testament',
    'abbrev': 'ot',
    'churchUri': '/scriptures/ot',
    'books': {
      'genesis': {
        'churchUri': '/scriptures/ot/gen',
        'churchChapters': [1],
        'bookGroup': 'Books of the Law',
      },
      #'exodus': {}, 'leviticus': {}, 'numbers': {}, 'deuteronomy': {}, 'joshua': {}, 'judges': {}, 'ruth': {}, '1-samuel': {}, '2-samuel': {}, '1-kings': {}, '2-kings': {}, '1-chronicles': {}, '2-chronicles': {}, 'ezra': {}, 'nehemiah': {}, 'esther': {}, 'job': {},
      'psalms': {
        'churchUri': '/scriptures/ot/ps',
        'churchChapters': [119],
        'bookGroup': 'Wisdom and Poetry',
      },
      'tobit': {
        'churchUri': None,
        'churchChapters': [],
        'bookGroup': 'Deuterocanonical Books',
      },
    },
  },
  'new-testament': {
    'name': 'New Testament',
    'abbrev': 'nt',
    'churchUri': '/scriptures/nt',
    'books': {
      'matthew': {
        'churchUri': '/scriptures/nt/matt',
        'churchChapters': [1],
        'bookGroup': 'The Gospels',
      },
      'philippians': {
        'churchUri': '/scriptures/nt/philip',
        'churchChapters': [4],
        'bookGroup': 'Epistles',
      },
    },
  },
  'book-of-mormon': {
    'name': 'Book of Mormon',
    'abbrev': 'bom',
    'churchUri': '/scriptures/bofm',
    'books': {
      '1-nephi': {
        'churchUri': '/scriptures/bofm/1-ne',
        'churchChapters': [1, 3],
        'bookGroup': None,
      },
      'enos': {
        'churchUri': '/scriptures/bofm/enos',
        'churchChapters': [1],
        'bookGroup': None,
      },
      'alma': {
        'churchUri': '/scriptures/bofm/alma',
        'churchChapters': [17],
        'bookGroup': None,
      },
    },
  },
  'doctrine-and-covenants': {
    'name': 'Doctrine and Covenants',
    'abbrev': 'dc',
    'churchUri': '/scriptures/dc-testament',
    'books': {
      'sections': {
        'churchUri': '/scriptures/dc-testament/dc',
        'churchChapters': [1, 77, 84],
        'bookGroup': None,
      },
      'official-declarations': {
        'churchUri': '/scriptures/dc-testament/od',
        'churchChapters': [1, 2],
        'bookGroup': None,
      },
    },
  },
  'pearl-of-great-price': {
    'name': 'Pearl of Great Price',
    'abbrev': 'pgp',
    'churchUri': '/scriptures/pgp',
    'books': {
      'moses': {
        'churchUri': '/scriptures/pgp/moses',
        'churchChapters': [1],
        'bookGroup': None,
      },
      'abraham': {
        'churchUri': '/scriptures/pgp/abr',
        'churchChapters': [1, 'fac-3'],
        'bookGroup': None,
      },
      'joseph-smith-history': {
        'churchUri': '/scriptures/pgp/js-h',
        'churchChapters': [1],
        'bookGroup': None,
      },
    },
  },
  'jst-appendix': {
    'name': 'Joseph Smith Translation Appendix',
    'abbrev': 'jst',
    'churchUri': '/scriptures/jst',
    'books': {
      'jst-genesis': {
        'churchUri': '/scriptures/jst/jst-gen',
        'churchChapters': ['1-8', 9],
        'bookGroup': None,
      },
      'jst-psalms': {
        'churchUri': '/scriptures/jst/jst-ps',
        'churchChapters': [11],
        'bookGroup': None,
      },
    },
  },
}


# TEMPLATES

templates_directory = os.path.abspath(os.path.dirname(__file__))

# HTML template
with open(os.path.join(templates_directory, 'template-html.html'), 'r', encoding='utf-8') as f:
  html_template = f.read()

# CSS template
with open(os.path.join(templates_directory, 'template-css.css'), 'r', encoding='utf-8') as f:
  css_template = f.read()

# README template
with open(os.path.join(templates_directory, 'template-readme.txt'), 'r', encoding='utf-8') as f:
  readme_template = f.read()

# MySQL SQL template
with open(os.path.join(templates_directory, 'template-mysql.sql'), 'r', encoding='utf-8') as f:
  sql_mysql_template = f.read()

# SQLite SQL template
with open(os.path.join(templates_directory, 'template-sqlite.sql'), 'r', encoding='utf-8') as f:
  sql_sqlite_template = f.read()


# FUNCTIONS

# Convert a string with spaces (like 'Book of Mormon') to a slug (like 'book-of-mormon')
def slugify(text, delim='-'):
  if not text:
    text = ''
  punctuation_re = re.compile(r'\W+', flags=re.UNICODE)
  result = []
  for word in punctuation_re.split(text.lower()):
    word = normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8')
    if word:
      result.append(word)
  return delim.join(result)

# Create SQL insert statement for adding rows to a table
def create_sql_insert_statement(table_name, dict_list):
  statement = ''
  if dict_list:
    field_names = dict_list[0].keys()
    field_names_string = ', '.join(field_names)
    statement += f'INSERT INTO {table_name} ({field_names_string})\nVALUES\n'
    
    num_items = len(dict_list)
    for i, item in enumerate(dict_list):
      line_end_punctuation = ';' if (i == num_items - 1) else ','
      field_values_string = ', '.join([(str(value) if isinstance(value, int) else ('NULL' if value is None else f'\'{value}\'')) for value in item.values()])
      statement += f'  ({field_values_string}){line_end_punctuation}\n'
      
    statement += '\n'
  return statement
