import os
import re
from unicodedata import normalize


# MAPPINGS

# A few book slugs need to be converted to singular when being used as part of a chapter slug
mapping_book_to_singular_slug = {
  'psalms': 'psalm',
  'sections': 'doctrine-and-covenants',
  'official-declarations': 'official-declaration',
  'facsimiles': 'facsimile',
  'jst-psalms': 'jst-psalm',
}

# Church content uses three-letter codes that are based on ISO 639-3 (but not fully compliant). This dictionary provides a mapping from industry-standard BCP 47 language tags to Church language codes.
mapping_bcp47_to_church_lang = { 'aa': 'aar', 'af': 'afr', 'am': 'amh', 'amu': 'amu', 'apw': 'apw', 'ar': 'ara', 'ar-Latn': 'ara-Latn', 'ase': 'ase', 'asf': 'asf', 'awa': 'awa', 'ay': 'aym', 'bad': 'bad', 'bci': 'bci', 'be': 'bel', 'bem': 'bem', 'bfa': 'bfa', 'bfi': 'bfi', 'bg': 'bul', 'bi': 'bis', 'bik': 'bik', 'bla': 'bla', 'bm': 'bam', 'bn': 'ben', 'bn-Latn': 'ben-Latn', 'bnt': 'bnt', 'bs': 'bos', 'bxg': 'bxg', 'ca': 'cat', 'cag': 'cag', 'cak': 'cak', 'cco': 'cco', 'ceb': 'ceb', 'ch': 'cha', 'chk': 'chk', 'cho': 'cho', 'chr': 'chr', 'chy': 'chy', 'ckw': 'ckw', 'cmn': 'cmn', 'cmn-Hans': 'zhs', 'cmn-Hant': 'zho', 'cmn-Latn': 'cmn-Latn', 'cs': 'ces', 'cu': 'chu', 'cuk': 'cuk', 'cy': 'cym', 'da': 'dan', 'dak': 'dak', 'de': 'deu', 'dv': 'div', 'ee': 'ewe', 'efi': 'efi', 'el': 'ell', 'el-Latn': 'ell-Latn', 'en': 'eng', 'en-Brai': 'eng-Brai', 'en-Dsrt': 'eng-Dsrt', 'en-GB': 'eng-GB', 'es': 'spa', 'es-419': 'spa-419', 'es-Brai': 'spa-Brai', 'es-ES': 'esp', 'es-MX': 'spa-MX', 'esk': 'esk', 'et': 'est', 'eu': 'eus', 'fan': 'fan', 'fat': 'fat', 'ff': 'ful', 'fi': 'fin', 'fj': 'fij', 'fon': 'fon', 'fr': 'fra', 'fr-HT': 'fra-HT', 'fr-PF': 'fra-PF', 'fuf': 'fuf', 'fy': 'fry', 'ga': 'gle', 'gaa': 'gaa', 'gd': 'gla', 'gil': 'gil', 'gl': 'glg', 'gn': 'grn', 'gpe': 'gpe', 'gul': 'gul', 'guz': 'guz', 'ha': 'hau', 'haw': 'haw', 'he': 'heb', 'he-Latn': 'heb-Latn', 'hi': 'hin', 'hi-Latn': 'hin-Latn', 'hif': 'hif', 'hil': 'hil', 'hmn': 'hmn', 'hr': 'hrv', 'ht': 'hat', 'hu': 'hun', 'hwc': 'hwc', 'hy': 'hye', 'hy-Latn': 'hye-Latn', 'hyw': 'hyw', 'iba': 'iba', 'id': 'ind', 'ig': 'ibo', 'ilo': 'ilo', 'iro': 'iro', 'is': 'isl', 'it': 'ita', 'ja': 'jpn', 'ja-Hani': 'jpn-Hani', 'ja-Hira': 'jpn-Hira', 'ja-Latn': 'jpn-Latn', 'jac': 'jac', 'jam': 'jam', 'jv': 'jav', 'ka': 'kat', 'kam': 'kam', 'kea': 'kea', 'kek': 'kek', 'kg': 'kon', 'kio': 'kio', 'kk': 'kaz', 'km': 'khm', 'km-Latn': 'khm-Latn', 'kn': 'kan', 'ko': 'kor', 'ko-Latn': 'kor-Latn', 'kos': 'kos', 'kpe': 'kpe', 'ksw': 'ksw', 'ku': 'kur', 'la': 'lat', 'lg': 'lug', 'lkt': 'lkt', 'ln': 'lin', 'lo': 'lao', 'lom': 'lom', 'lou': 'lou', 'lt': 'lit', 'lua': 'lua', 'luo': 'luo', 'lv': 'lav', 'mam': 'mam', 'meu': 'meu', 'mfe': 'mfe', 'mg': 'mlg', 'mh': 'mah', 'mi': 'mri', 'mis': 'mis', 'mk': 'mkd', 'ml': 'mal', 'mn': 'mon', 'mnk': 'mnk', 'mos': 'mos', 'mr': 'mar', 'ms': 'msa', 'mt': 'mlt', 'mul': 'mul', 'mus': 'mus', 'mvc': 'mvc', 'my': 'mya', 'nds': 'nds', 'ne': 'nep', 'ngu': 'ngu', 'niu': 'niu', 'nl': 'nld', 'no': 'nor', 'nr': 'nbl', 'nso': 'nso', 'nv': 'nav', 'ny': 'nya', 'oj': 'oji', 'om': 'orm', 'om-Ethi': 'orm-Ethi', 'oma': 'oma', 'or': 'ori', 'pa': 'pan', 'pag': 'pag', 'pam': 'pam', 'pap': 'pap', 'pau': 'pau', 'paw': 'paw', 'pes': 'pes', 'pga': 'pga', 'pis': 'pis', 'pl': 'pol', 'poh': 'pob', 'pon': 'pon', 'ppl': 'ppl', 'ps': 'pus', 'pt': 'por', 'pt-BR': 'por-BR', 'pt-PT': 'ept', 'qu': 'que', 'quc': 'quc', 'quh': 'quh', 'quz': 'quz', 'qvi': 'qvi', 'rar': 'rar', 'rn': 'run', 'ro': 'ron', 'rtm': 'rtm', 'ru': 'rus', 'ru-Latn': 'rus-Latn', 'ru-x-stress': 'rus-x-stress', 'rw': 'kin', 'si': 'sin', 'sk': 'slk', 'sl': 'slv', 'sm': 'smo', 'sn': 'sna', 'so': 'som', 'sq': 'alb', 'sr': 'srp', 'srb': 'srb', 'srn': 'srn', 'ss': 'ssw', 'st': 'sot', 'ste': 'ste', 'sto': 'sto', 'sv': 'swe', 'sw': 'swa', 'swc': 'swc', 'syc': 'syc', 'ta': 'tam', 'ta-Latn': 'tam-Latn', 'te': 'tel', 'te-Latn': 'tel-Latn', 'th': 'tha', 'th-Latn': 'tha-Latn', 'tl': 'tgl', 'tn': 'tsn', 'to': 'ton', 'tpi': 'tpi', 'tr': 'tur', 'tr-Armn': 'tur-Armn', 'tvl': 'tvl', 'tw': 'twi', 'ty': 'tah', 'tzj': 'tzj', 'tzo': 'tzo', 'uk': 'ukr', 'und': 'und', 'ur': 'urd', 'usp': 'usp', 'uz': 'uzb', 'vi': 'vie', 'war': 'war', 'wo': 'wol', 'wyn': 'wyn', 'xh': 'xho', 'yap': 'yap', 'yi': 'yid', 'yi-Latn': 'yid-Latn', 'yo': 'yor', 'yua': 'yua', 'yue': 'yue', 'yue-Hant': 'yue', 'yue-Latn': 'yue-Latn', 'zdj': 'zdj', 'zh': 'zho', 'zh-Hans': 'zhs', 'zh-Hant': 'zho', 'zh-Latn': 'zho-Latn', 'zh-Latn-TW': 'zho-Latn-TW', 'zh-TW': 'zho-TW', 'znd': 'znd', 'zu': 'zul', 'zun': 'zun', 'zxx': 'zxx' }

# Map from BCP 47 language tags to English language names
mapping_bcp47_to_english_name = { 'aa': 'Afar', 'af': 'Afrikaans', 'am': 'Amharic', 'amu': 'Amuzgo (Guerrero)', 'apw': 'Apache (Western)', 'ar': 'Arabic', 'ar-Latn': 'Arabic (Romanized)', 'ase': 'American Sign Language (ASL)', 'asf': 'Australian Sign Language (Auslan)', 'awa': 'Awadhi', 'ay': 'Aymara', 'bad': 'Banda', 'bci': 'Baule', 'be': 'Belarusian', 'bem': 'Bemba', 'bfa': 'Bari', 'bfi': 'British Sign Language (BSL)', 'bg': 'Bulgarian', 'bi': 'Bislama', 'bik': 'Bikolano', 'bla': 'Blackfoot', 'bm': 'Bambara', 'bn': 'Bengali', 'bn-Latn': 'Bengali (Romanized)', 'bnt': 'Bantu', 'bs': 'Bosnian', 'bxg': 'Bangala', 'ca': 'Catalan', 'cag': 'Nivaclé', 'cak': 'Kaqchikel (Cakchiquel)', 'cco': 'Chinantec (Comaltepec)', 'ceb': 'Cebuano', 'ch': 'Chamorro', 'chk': 'Chuukese', 'cho': 'Choctaw', 'chr': 'Cherokee', 'chy': 'Cheyenne', 'ckw': 'Kaqchikel (Occidental)', 'cmn': 'Mandarin', 'cmn-Hans': 'Mandarin (Simplified)', 'cmn-Hant': 'Mandarin (Traditional)', 'cmn-Latn': 'Mandarin (Romanized/Pinyin)', 'cs': 'Czech', 'cu': 'Church Slavonic', 'cuk': 'Kuna', 'cy': 'Welsh', 'da': 'Danish', 'dak': 'Dakota', 'de': 'German', 'dv': 'Dhivehi', 'ee': 'Ewe', 'efi': 'Efik', 'el': 'Greek', 'el-Latn': 'Greek (Romanized)', 'en': 'English', 'en-Brai': 'English Braille', 'en-Dsrt': 'English Deseret', 'en-GB': 'English (UK)', 'es': 'Spanish', 'es-419': 'Spanish (Latin America)', 'es-Brai': 'Spanish Braille', 'es-ES': 'Spanish (Spain)', 'es-MX': 'Spanish (Mexico)', 'esk': 'Eskimo', 'et': 'Estonian', 'eu': 'Basque', 'fan': 'Fang', 'fat': 'Fante', 'ff': 'Fulah', 'fi': 'Finnish', 'fj': 'Fijian', 'fon': 'Fon', 'fr': 'French', 'fr-HT': 'French (Haiti)', 'fr-PF': 'French (French Polynesia)', 'fuf': 'Pular', 'fy': 'Frisian (West)', 'ga': 'Irish', 'gaa': 'Ga', 'gd': 'Gaelic', 'gil': 'Kiribati (Gilbertese)', 'gl': 'Galician', 'gn': 'Guarani', 'gpe': 'Ghanaian', 'gul': 'Gullah', 'guz': 'Gusii (Kisii)', 'ha': 'Hausa', 'haw': 'Hawaiian', 'he': 'Hebrew', 'he-Latn': 'Hebrew (Romanized)', 'hi': 'Hindi', 'hi-Latn': 'Hindi (Romanized)', 'hif': 'Hindi (Fiji)', 'hil': 'Hiligaynon', 'hmn': 'Hmong', 'hr': 'Croatian', 'ht': 'Haitian Creole', 'hu': 'Hungarian', 'hwc': 'Hawaiian Pidgin', 'hy': 'Armenian (East)', 'hy-Latn': 'Armenian (Romanized)', 'hyw': 'Armenian (West)', 'iba': 'Iban', 'id': 'Indonesian', 'ig': 'Igbo', 'ilo': 'Ilokano', 'iro': 'Iroquoian', 'is': 'Icelandic', 'it': 'Italian', 'ja': 'Japanese', 'ja-Hani': 'Japanese (Kanji)', 'ja-Hira': 'Japanese (Hiragana)', 'ja-Latn': 'Japanese (Romanized/Romanji)', 'jac': 'Jakaltek (Oriental)', 'jam': 'Patois (Jamaica)', 'jv': 'Javanese', 'ka': 'Georgian', 'kam': 'Kamba', 'kea': 'Creole (Cape Verde)', 'kek': 'Kekchi', 'kg': 'Kongo (Kikongo)', 'kio': 'Kiowa', 'kk': 'Kazakh', 'km': 'Khmer (Cambodian)', 'km-Latn': 'Khmer (Cambodian) (Romanized)', 'kn': 'Kannada', 'ko': 'Korean', 'ko-Latn': 'Korean (Romanized)', 'kos': 'Kosraean', 'kpe': 'Kpelle', 'ksw': 'Karen', 'ku': 'Kurdish', 'la': 'Latin', 'lg': 'Lugandan', 'lkt': 'Lakota', 'ln': 'Lingala', 'lo': 'Laotian', 'lom': 'Loma', 'lou': 'Louisiana Creole', 'lt': 'Lithuanian', 'lua': 'Tshiluba', 'luo': 'Dholuo', 'lv': 'Latvian', 'mam': 'Mam', 'meu': 'Motu', 'mfe': 'Mauritian Creole', 'mg': 'Malagasy', 'mh': 'Marshallese', 'mi': 'Maori', 'mis': 'Narration', 'mk': 'Macedonian', 'ml': 'Malayalam', 'mn': 'Mongolian', 'mnk': 'Mandinka', 'mos': 'Mossi', 'mr': 'Marathi', 'ms': 'Malay', 'mt': 'Maltese', 'mul': 'Multiple languages', 'mus': 'Muscogee', 'mvc': 'Mam (Central)', 'my': 'Burmese (Myanmar)', 'nds': 'German (Low)', 'ne': 'Nepali', 'ngu': 'Nahuatl (Guerrero)', 'niu': 'Niuean', 'nl': 'Dutch', 'no': 'Norwegian', 'nr': 'Ndebele (Southern)', 'nso': 'Sotho (Northern)', 'nv': 'Navajo', 'ny': 'Chewa', 'oj': 'Ojibwe', 'om': 'Oromo', 'om-Ethi': 'Oromo (Ethiopic Script)', 'oma': 'Omaha', 'or': 'Odia (Oriya)', 'pa': 'Punjabi', 'pag': 'Pangasinan', 'pam': 'Pampango (Kapampangan)', 'pap': 'Papiamento', 'pau': 'Palauan', 'paw': 'Pawnee', 'pes': 'Persian (Iran) (Farsi)', 'pga': 'Arabic (Juba)', 'pis': 'Pidgin (Solomon Islands)', 'pl': 'Polish', 'poh': 'Poqomchiʼ', 'pon': 'Pohnpeian', 'ppl': 'Nawat (Pipil)', 'ps': 'Pashto', 'pt': 'Portuguese', 'pt-BR': 'Portuguese (Brazil)', 'pt-PT': 'Portuguese (Portugal)', 'qu': 'Quichua', 'quc': 'Quiche', 'quh': 'Quechua (Bolivia)', 'quz': 'Quechua (Peru)', 'qvi': 'Quichua (Ecuador)', 'rar': 'Rarotongan (Cook Islands Maori)', 'rn': 'Rundi', 'ro': 'Romanian', 'rtm': 'Rotuman', 'ru': 'Russian', 'ru-Latn': 'Russian (Romanized)', 'ru-x-stress': 'Russian (Stress Marks)', 'rw': 'Rwanda', 'si': 'Sinhala', 'sk': 'Slovak', 'sl': 'Slovenian', 'sm': 'Samoan', 'sn': 'Shona', 'so': 'Somali', 'sq': 'Albanian', 'sr': 'Serbian', 'srb': 'Sora', 'srn': 'Sranan', 'ss': 'Swazi', 'st': 'Sotho (Southern)', 'ste': 'Liana', 'sto': 'Stoney Nakoda', 'sv': 'Swedish', 'sw': 'Swahili', 'swc': 'Swahili (Congo)', 'syc': 'Syriac', 'ta': 'Tamil', 'ta-Latn': 'Tamil (Romanized)', 'te': 'Telugu', 'te-Latn': 'Telugu (Romanized)', 'th': 'Thai', 'th-Latn': 'Thai (Romanized)', 'tl': 'Tagalog', 'tn': 'Tswana (Setswana)', 'to': 'Tongan', 'tpi': 'Tok Pisin (Neomelanesian)', 'tr': 'Turkish', 'tr-Armn': 'Turkish (Armenian Script)', 'tvl': 'Tuvalu', 'tw': 'Twi', 'ty': 'Tahitian', 'tzj': 'Tz’utujil', 'tzo': 'Tzotzil', 'uk': 'Ukrainian', 'und': 'Undetermined', 'ur': 'Urdu', 'usp': 'Uspantek', 'uz': 'Uzbek', 'vi': 'Vietnamese', 'war': 'Waray', 'wo': 'Wolof', 'wyn': 'Wyandot', 'xh': 'Xhosa', 'yap': 'Yapese', 'yi': 'Yiddish', 'yi-Latn': 'Yiddish (Romanized)', 'yo': 'Yoruba', 'yua': 'Maya (Yucatec)', 'yue': 'Cantonese', 'yue-Hant': 'Cantonese (Traditional)', 'yue-Latn': 'Cantonese (Romanized/Pingyam)', 'zdj': 'Comorian', 'zh': 'Chinese', 'zh-Hans': 'Chinese (Simplified)', 'zh-Hant': 'Chinese (Traditional)', 'zh-Latn': 'Chinese (Romanized)', 'zh-Latn-TW': 'Taiwanese (Romanized)', 'zh-TW': 'Taiwanese', 'znd': 'Ngala (Zande)', 'zu': 'Zulu', 'zun': 'Zuni', 'zxx': 'Instrumental' }

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
