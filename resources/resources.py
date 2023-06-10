import os

working_directory = os.path.abspath(os.path.dirname(__file__))

# A few book slugs need to be converted to singular when being used as part of a chapter slug
mapping_plural_to_singular_book_slug = {
  'psalms': 'psalm',
  'sections': 'section',
  'official-declarations': 'official-declaration',
}

# Church content uses three-letter codes that are based on ISO 639-3 (but not fully compliant). This dictionary provides a mapping from Church language codes to industry-standard BCP 47 language tags.
mapping_church_lang_to_bcp47 = { 'afr': 'af', 'alb': 'sq', 'amh': 'am', 'amu': 'amu', 'apw': 'apw', 'ara': 'ar', 'ase': 'ase', 'asf': 'asf', 'awa': 'awa', 'aym': 'ay', 'bam': 'bm', 'bel': 'be', 'bem': 'bem', 'ben': 'bn', 'bik': 'bik', 'bis': 'bi', 'bla': 'bla', 'bos': 'bs', 'bul': 'bg', 'cag': 'cag', 'cak': 'cak', 'cat': 'ca', 'cco': 'cco', 'ceb': 'ceb', 'ces': 'cs', 'cha': 'ch', 'chk': 'chk', 'chr': 'chr', 'ckw': 'ckw', 'cmn': 'cmn', 'cuk': 'cuk', 'cym': 'cy', 'dan': 'da', 'deu': 'de', 'efi': 'efi', 'ell': 'el', 'eng': 'en', 'ept': 'pt-PT', 'esp': 'es-ES', 'est': 'et', 'eus': 'eu', 'fat': 'fat', 'fij': 'fj', 'fin': 'fi', 'fon': 'fon', 'fra': 'fr', 'frp': 'fr-PF', 'gil': 'gil', 'gla': 'gd', 'gle': 'ga', 'grn': 'gn', 'guz': 'guz', 'hat': 'ht', 'haw': 'haw', 'heb': 'he', 'hif': 'hif', 'hil': 'hil', 'hin': 'hi', 'hmn': 'hmn', 'hmo': 'ho', 'hrv': 'hr', 'hun': 'hu', 'hwc': 'hwc', 'hye': 'hy', 'hyw': 'hyw', 'iba': 'iba', 'ibo': 'ig', 'ilo': 'ilo', 'ind': 'id', 'isl': 'is', 'ita': 'it', 'jac': 'jac', 'jav': 'jv', 'jpn': 'ja', 'kam': 'kam', 'kan': 'kn', 'kat': 'ka', 'kaz': 'kk', 'kek': 'kek', 'khm': 'km', 'kin': 'rw', 'kon': 'kg', 'kor': 'ko', 'kos': 'kos', 'kpe': 'kpe', 'ksw': 'ksw', 'kur': 'ku', 'lao': 'lo', 'lat': 'la', 'lav': 'lv', 'lin': 'ln', 'lit': 'lt', 'lua': 'lua', 'luo': 'luo', 'mah': 'mh', 'mal': 'ml', 'mam': 'mam', 'mar': 'mr', 'meu': 'meu', 'mfe': 'mfe', 'mis': 'mis', 'mkd': 'mk', 'mlg': 'mg', 'mlt': 'mt', 'mnk': 'mnk', 'mon': 'mn', 'mos': 'mos', 'mri': 'mi', 'msa': 'ms', 'mul': 'mul', 'mvc': 'mvc', 'mya': 'my', 'nav': 'nv', 'nbl': 'nr', 'nds': 'nds', 'nep': 'ne', 'ngu': 'ngu', 'niu': 'niu', 'nld': 'nl', 'nor': 'no', 'nso': 'nso', 'nya': 'ny', 'ori': 'or', 'orm': 'om', 'pag': 'pag', 'pam': 'pam', 'pan': 'pa', 'pap': 'pap', 'pau': 'pau', 'pes': 'fa', 'pol': 'pl', 'pon': 'pon', 'por': 'pt', 'ppl': 'ppl', 'quc': 'quc', 'que': 'qu', 'quh': 'quh', 'quz': 'quz', 'qvi': 'qvi', 'rar': 'rar', 'ron': 'ro', 'rtm': 'rtm', 'rus': 'ru', 'sin': 'si', 'slk': 'sk', 'slv': 'sl', 'smo': 'sm', 'sna': 'sn', 'som': 'so', 'sot': 'st', 'spa': 'es', 'srb': 'srb', 'srp': 'sr', 'ssw': 'ss', 'sto': 'sto', 'swa': 'sw', 'swe': 'sv', 'tah': 'ty', 'tam': 'ta', 'tel': 'te', 'tgl': 'tl', 'tha': 'th', 'ton': 'to', 'tpi': 'tpi', 'tsn': 'tn', 'tur': 'tr', 'tvl': 'tvl', 'twi': 'tw', 'tzj': 'tzj', 'tzo': 'tzo', 'ukr': 'uk', 'und': 'und', 'urd': 'ur', 'usp': 'usp', 'uzb': 'uz', 'vie': 'vi', 'war': 'war', 'wol': 'wo', 'xho': 'xh', 'yap': 'yap', 'yor': 'yo', 'yua': 'yua', 'yue': 'yue-Hant', 'zdj': 'zdj', 'zho': 'cmn-Hant', 'zhs': 'cmn-Hans', 'zul': 'zu', 'zxx': 'zxx' }

# Mapping from BCP 47 language tags to Church language codes
mapping_bcp47_to_church_lang = { 'af': 'afr', 'am': 'amh', 'amu': 'amu', 'apw': 'apw', 'ar': 'ara', 'ase': 'ase', 'asf': 'asf', 'awa': 'awa', 'ay': 'aym', 'be': 'bel', 'bem': 'bem', 'bg': 'bul', 'bi': 'bis', 'bik': 'bik', 'bla': 'bla', 'bm': 'bam', 'bn': 'ben', 'bs': 'bos', 'ca': 'cat', 'cag': 'cag', 'cak': 'cak', 'cco': 'cco', 'ceb': 'ceb', 'ch': 'cha', 'chk': 'chk', 'chr': 'chr', 'ckw': 'ckw', 'cmn-Hans': 'zhs', 'cmn-Hant': 'zho', 'cmn': 'cmn', 'cs': 'ces', 'cuk': 'cuk', 'cy': 'cym', 'da': 'dan', 'de': 'deu', 'efi': 'efi', 'el': 'ell', 'en': 'eng', 'es-ES': 'esp', 'es': 'spa', 'et': 'est', 'eu': 'eus', 'fa': 'pes', 'fat': 'fat', 'fi': 'fin', 'fj': 'fij', 'fon': 'fon', 'fr-PF': 'frp', 'fr': 'fra', 'ga': 'gle', 'gd': 'gla', 'gil': 'gil', 'gn': 'grn', 'guz': 'guz', 'haw': 'haw', 'he': 'heb', 'hi': 'hin', 'hif': 'hif', 'hil': 'hil', 'hmn': 'hmn', 'ho': 'hmo', 'hr': 'hrv', 'ht': 'hat', 'hu': 'hun', 'hwc': 'hwc', 'hy': 'hye', 'hyw': 'hyw', 'iba': 'iba', 'id': 'ind', 'ig': 'ibo', 'ilo': 'ilo', 'is': 'isl', 'it': 'ita', 'ja': 'jpn', 'jac': 'jac', 'jv': 'jav', 'ka': 'kat', 'kam': 'kam', 'kek': 'kek', 'kg': 'kon', 'kk': 'kaz', 'km': 'khm', 'kn': 'kan', 'ko': 'kor', 'kos': 'kos', 'kpe': 'kpe', 'ksw': 'ksw', 'ku': 'kur', 'la': 'lat', 'ln': 'lin', 'lo': 'lao', 'lt': 'lit', 'lua': 'lua', 'luo': 'luo', 'lv': 'lav', 'mam': 'mam', 'meu': 'meu', 'mfe': 'mfe', 'mg': 'mlg', 'mh': 'mah', 'mi': 'mri', 'mis': 'mis', 'mk': 'mkd', 'ml': 'mal', 'mn': 'mon', 'mnk': 'mnk', 'mos': 'mos', 'mr': 'mar', 'ms': 'msa', 'mt': 'mlt', 'mul': 'mul', 'mvc': 'mvc', 'my': 'mya', 'nds': 'nds', 'ne': 'nep', 'ngu': 'ngu', 'niu': 'niu', 'nl': 'nld', 'no': 'nor', 'nr': 'nbl', 'nso': 'nso', 'nv': 'nav', 'ny': 'nya', 'om': 'orm', 'or': 'ori', 'pa': 'pan', 'pag': 'pag', 'pam': 'pam', 'pap': 'pap', 'pau': 'pau', 'pl': 'pol', 'pon': 'pon', 'ppl': 'ppl', 'pt-PT': 'ept', 'pt': 'por', 'qu': 'que', 'quc': 'quc', 'quh': 'quh', 'quz': 'quz', 'qvi': 'qvi', 'rar': 'rar', 'ro': 'ron', 'rtm': 'rtm', 'ru': 'rus', 'rw': 'kin', 'si': 'sin', 'sk': 'slk', 'sl': 'slv', 'sm': 'smo', 'sn': 'sna', 'so': 'som', 'sq': 'alb', 'sr': 'srp', 'srb': 'srb', 'ss': 'ssw', 'st': 'sot', 'sto': 'sto', 'sv': 'swe', 'sw': 'swa', 'ta': 'tam', 'te': 'tel', 'th': 'tha', 'tl': 'tgl', 'tn': 'tsn', 'to': 'ton', 'tpi': 'tpi', 'tr': 'tur', 'tvl': 'tvl', 'tw': 'twi', 'ty': 'tah', 'tzj': 'tzj', 'tzo': 'tzo', 'uk': 'ukr', 'und': 'und', 'ur': 'urd', 'usp': 'usp', 'uz': 'uzb', 'vi': 'vie', 'war': 'war', 'wo': 'wol', 'xh': 'xho', 'yap': 'yap', 'yo': 'yor', 'yua': 'yua', 'yue-Hant': 'yue', 'zdj': 'zdj', 'zu': 'zul', 'zxx': 'zxx' }

# Data for volumes, books, and chapters of scripture
metadata_structure = {
  'old-testament': {
    'name': 'Old Testament',
    'abbrev': 'OT',
    'churchUri': '/scriptures/ot',
    'numBooks': 39,
    'books': {
      'genesis': {
        'churchUri': '/scriptures/ot/gen',
        'numberedChapters': 50,
        'namedChapters': [],
      },
      'exodus': {
        'churchUri': '/scriptures/ot/ex',
        'numberedChapters': 40,
        'namedChapters': [],
      },
      'leviticus': {
        'churchUri': '/scriptures/ot/lev',
        'numberedChapters': 27,
        'namedChapters': [],
      },
      'numbers': {
        'churchUri': '/scriptures/ot/num',
        'numberedChapters': 36,
        'namedChapters': [],
      },
      'deuteronomy': {
        'churchUri': '/scriptures/ot/deut',
        'numberedChapters': 34,
        'namedChapters': [],
      },
      'joshua': {
        'churchUri': '/scriptures/ot/josh',
        'numberedChapters': 24,
        'namedChapters': [],
      },
      'judges': {
        'churchUri': '/scriptures/ot/judg',
        'numberedChapters': 21,
        'namedChapters': [],
      },
      'ruth': {
        'churchUri': '/scriptures/ot/ruth',
        'numberedChapters': 4,
        'namedChapters': [],
      },
      '1-samuel': {
        'churchUri': '/scriptures/ot/1-sam',
        'numberedChapters': 31,
        'namedChapters': [],
      },
      '2-samuel': {
        'churchUri': '/scriptures/ot/2-sam',
        'numberedChapters': 24,
        'namedChapters': [],
      },
      '1-kings': {
        'churchUri': '/scriptures/ot/1-kgs',
        'numberedChapters': 22,
        'namedChapters': [],
      },
      '2-kings': {
        'churchUri': '/scriptures/ot/2-kgs',
        'numberedChapters': 25,
        'namedChapters': [],
      },
      '1-chronicles': {
        'churchUri': '/scriptures/ot/1-chr',
        'numberedChapters': 29,
        'namedChapters': [],
      },
      '2-chronicles': {
        'churchUri': '/scriptures/ot/2-chr',
        'numberedChapters': 36,
        'namedChapters': [],
      },
      'ezra': {
        'churchUri': '/scriptures/ot/ezra',
        'numberedChapters': 10,
        'namedChapters': [],
      },
      'nehemiah': {
        'churchUri': '/scriptures/ot/neh',
        'numberedChapters': 13,
        'namedChapters': [],
      },
      'esther': {
        'churchUri': '/scriptures/ot/esth',
        'numberedChapters': 10,
        'namedChapters': [],
      },
      'job': {
        'churchUri': '/scriptures/ot/job',
        'numberedChapters': 42,
        'namedChapters': [],
      },
      'psalms': {
        'churchUri': '/scriptures/ot/ps',
        'numberedChapters': 150,
        'namedChapters': [],
      },
      'proverbs': {
        'churchUri': '/scriptures/ot/prov',
        'numberedChapters': 31,
        'namedChapters': [],
      },
      'ecclesiastes': {
        'churchUri': '/scriptures/ot/eccl',
        'numberedChapters': 12,
        'namedChapters': [],
      },
      'song-of-solomon': {
        'churchUri': '/scriptures/ot/song',
        'numberedChapters': 8,
        'namedChapters': [],
      },
      'isaiah': {
        'churchUri': '/scriptures/ot/isa',
        'numberedChapters': 66,
        'namedChapters': [],
      },
      'jeremiah': {
        'churchUri': '/scriptures/ot/jer',
        'numberedChapters': 52,
        'namedChapters': [],
      },
      'lamentations': {
        'churchUri': '/scriptures/ot/lam',
        'numberedChapters': 5,
        'namedChapters': [],
      },
      'ezekiel': {
        'churchUri': '/scriptures/ot/ezek',
        'numberedChapters': 48,
        'namedChapters': [],
      },
      'daniel': {
        'churchUri': '/scriptures/ot/dan',
        'numberedChapters': 12,
        'namedChapters': [],
      },
      'hosea': {
        'churchUri': '/scriptures/ot/hosea',
        'numberedChapters': 14,
        'namedChapters': [],
      },
      'joel': {
        'churchUri': '/scriptures/ot/joel',
        'numberedChapters': 3,
        'namedChapters': [],
      },
      'amos': {
        'churchUri': '/scriptures/ot/amos',
        'numberedChapters': 9,
        'namedChapters': [],
      },
      'obadiah': {
        'churchUri': '/scriptures/ot/obad',
        'numberedChapters': 1,
        'namedChapters': [],
      },
      'jonah': {
        'churchUri': '/scriptures/ot/jonah',
        'numberedChapters': 4,
        'namedChapters': [],
      },
      'micah': {
        'churchUri': '/scriptures/ot/micah',
        'numberedChapters': 7,
        'namedChapters': [],
      },
      'nahum': {
        'churchUri': '/scriptures/ot/nahum',
        'numberedChapters': 3,
        'namedChapters': [],
      },
      'habakkuk': {
        'churchUri': '/scriptures/ot/hab',
        'numberedChapters': 3,
        'namedChapters': [],
      },
      'zephaniah': {
        'churchUri': '/scriptures/ot/zeph',
        'numberedChapters': 3,
        'namedChapters': [],
      },
      'haggai': {
        'churchUri': '/scriptures/ot/hag',
        'numberedChapters': 2,
        'namedChapters': [],
      },
      'zechariah': {
        'churchUri': '/scriptures/ot/zech',
        'numberedChapters': 14,
        'namedChapters': [],
      },
      'malachi': {
        'churchUri': '/scriptures/ot/mal',
        'numberedChapters': 4,
        'namedChapters': [],
      },
    },
  },
  'new-testament': {
    'name': 'New Testament',
    'abbrev': 'NT',
    'churchUri': '/scriptures/nt',
    'numBooks': 27,
    'books': {
      'matthew': {
        'churchUri': '/scriptures/nt/matt',
        'numberedChapters': 28,
        'namedChapters': [],
      },
      'mark': {
        'churchUri': '/scriptures/nt/mark',
        'numberedChapters': 16,
        'namedChapters': [],
      },
      'luke': {
        'churchUri': '/scriptures/nt/luke',
        'numberedChapters': 24,
        'namedChapters': [],
      },
      'john': {
        'churchUri': '/scriptures/nt/john',
        'numberedChapters': 21,
        'namedChapters': [],
      },
      'acts': {
        'churchUri': '/scriptures/nt/acts',
        'numberedChapters': 28,
        'namedChapters': [],
      },
      'romans': {
        'churchUri': '/scriptures/nt/rom',
        'numberedChapters': 16,
        'namedChapters': [],
      },
      '1-corinthians': {
        'churchUri': '/scriptures/nt/1-cor',
        'numberedChapters': 16,
        'namedChapters': [],
      },
      '2-corinthians': {
        'churchUri': '/scriptures/nt/2-cor',
        'numberedChapters': 13,
        'namedChapters': [],
      },
      'galations': {
        'churchUri': '/scriptures/nt/gal',
        'numberedChapters': 6,
        'namedChapters': [],
      },
      'ephesians': {
        'churchUri': '/scriptures/nt/eph',
        'numberedChapters': 6,
        'namedChapters': [],
      },
      'philippians': {
        'churchUri': '/scriptures/nt/philip',
        'numberedChapters': 4,
        'namedChapters': [],
      },
      'colossians': {
        'churchUri': '/scriptures/nt/col',
        'numberedChapters': 4,
        'namedChapters': [],
      },
      '1-thessalonians': {
        'churchUri': '/scriptures/nt/1-thes',
        'numberedChapters': 5,
        'namedChapters': [],
      },
      '2-thessalonians': {
        'churchUri': '/scriptures/nt/2-thes',
        'numberedChapters': 3,
        'namedChapters': [],
      },
      '1-timothy': {
        'churchUri': '/scriptures/nt/1-tim',
        'numberedChapters': 6,
        'namedChapters': [],
      },
      '2-timothy': {
        'churchUri': '/scriptures/nt/2-tim',
        'numberedChapters': 4,
        'namedChapters': [],
      },
      'titus': {
        'churchUri': '/scriptures/nt/titus',
        'numberedChapters': 3,
        'namedChapters': [],
      },
      'philemon': {
        'churchUri': '/scriptures/nt/philem',
        'numberedChapters': 1,
        'namedChapters': [],
      },
      'hebrews': {
        'churchUri': '/scriptures/nt/heb',
        'numberedChapters': 13,
        'namedChapters': [],
      },
      'james': {
        'churchUri': '/scriptures/nt/james',
        'numberedChapters': 5,
        'namedChapters': [],
      },
      '1-peter': {
        'churchUri': '/scriptures/nt/1-pet',
        'numberedChapters': 5,
        'namedChapters': [],
      },
      '2-peter': {
        'churchUri': '/scriptures/nt/2-pet',
        'numberedChapters': 3,
        'namedChapters': [],
      },
      '1-john': {
        'churchUri': '/scriptures/nt/1-jn',
        'numberedChapters': 5,
        'namedChapters': [],
      },
      '2-john': {
        'churchUri': '/scriptures/nt/2-jn',
        'numberedChapters': 1,
        'namedChapters': [],
      },
      '3-john': {
        'churchUri': '/scriptures/nt/3-jn',
        'numberedChapters': 1,
        'namedChapters': [],
      },
      'jude': {
        'churchUri': '/scriptures/nt/jude',
        'numberedChapters': 1,
        'namedChapters': [],
      },
      'revelation': {
        'churchUri': '/scriptures/nt/rev',
        'numberedChapters': 22,
        'namedChapters': [],
      },
    },
  },
  'book-of-mormon': {
    'name': 'Book of Mormon',
    'abbrev': 'BofM',
    'churchUri': '/scriptures/bofm',
    'numBooks': 15,
    'books': {
      '1-nephi': {
        'churchUri': '/scriptures/bofm/1-ne',
        'numberedChapters': 22,
        'namedChapters': [],
      },
      '2-nephi': {
        'churchUri': '/scriptures/bofm/2-ne',
        'numberedChapters': 33,
        'namedChapters': [],
      },
      'jacob': {
        'churchUri': '/scriptures/bofm/jacob',
        'numberedChapters': 7,
        'namedChapters': [],
      },
      'enos': {
        'churchUri': '/scriptures/bofm/enos',
        'numberedChapters': 1,
        'namedChapters': [],
      },
      'jarom': {
        'churchUri': '/scriptures/bofm/jarom',
        'numberedChapters': 1,
        'namedChapters': [],
      },
      'omni': {
        'churchUri': '/scriptures/bofm/omni',
        'numberedChapters': 1,
        'namedChapters': [],
      },
      'words-of-mormon': {
        'churchUri': '/scriptures/bofm/w-of-m',
        'numberedChapters': 1,
        'namedChapters': [],
      },
      'mosiah': {
        'churchUri': '/scriptures/bofm/mosiah',
        'numberedChapters': 29,
        'namedChapters': [],
      },
      'alma': {
        'churchUri': '/scriptures/bofm/alma',
        'numberedChapters': 63,
        'namedChapters': [],
      },
      'helaman': {
        'churchUri': '/scriptures/bofm/hel',
        'numberedChapters': 16,
        'namedChapters': [],
      },
      '3-nephi': {
        'churchUri': '/scriptures/bofm/3-ne',
        'numberedChapters': 30,
        'namedChapters': [],
      },
      '4-nephi': {
        'churchUri': '/scriptures/bofm/4-ne',
        'numberedChapters': 1,
        'namedChapters': [],
      },
      'mormon': {
        'churchUri': '/scriptures/bofm/morm',
        'numberedChapters': 9,
        'namedChapters': [],
      },
      'ether': {
        'churchUri': '/scriptures/bofm/ether',
        'numberedChapters': 15,
        'namedChapters': [],
      },
      'moroni': {
        'churchUri': '/scriptures/bofm/moro',
        'numberedChapters': 10,
        'namedChapters': [],
      },
    },
  },
  'doctrine-and-covenants': {
    'name': 'Doctrine and Covenants',
    'abbrev': 'D&C',
    'churchUri': '/scriptures/dc-testament',
    'numBooks': 2,
    'books': {
      'sections': {
        'churchUri': '/scriptures/dc-testament/dc',
        'numberedChapters': 138,
        'namedChapters': [],
      },
      'official-declarations': {
        'churchUri': '/scriptures/dc-testament/od',
        'numberedChapters': 2,
        'namedChapters': [],
      },
    },
  },
  'pearl-of-great-price': {
    'name': 'Pearl of Great Price',
    'abbrev': 'PGP',
    'churchUri': '/scriptures/pgp',
    'numBooks': 5,
    'books': {
      'moses': {
        'churchUri': '/scriptures/pgp/moses',
        'numberedChapters': 8,
        'namedChapters': [],
      },
      'abraham': {
        'churchUri': '/scriptures/pgp/abr',
        'numberedChapters': 5,
        'namedChapters': ['fac-1', 'fac-2', 'fac-3'],
      },
      'joseph-smith-matthew': {
        'churchUri': '/scriptures/pgp/js-m',
        'numberedChapters': 1,
        'namedChapters': [],
      },
      'joseph-smith-history': {
        'churchUri': '/scriptures/pgp/js-h',
        'numberedChapters': 1,
        'namedChapters': [],
      },
      'articles-of-faith': {
        'churchUri': '/scriptures/pgp/a-of-f',
        'numberedChapters': 1,
        'namedChapters': [],
      },
    },
  },
}

# Test data (only a few books and chapters are included, for faster testing)
test_data_structure = {
  'old-testament': {
    'name': 'Old Testament',
    'abbrev': 'OT',
    'churchUri': '/scriptures/ot',
    'numBooks': 2,
    'books': {
      'genesis': {
        'churchUri': '/scriptures/ot/gen',
        'numberedChapters': 0,
        'namedChapters': ['1'],
      },
      'psalms': {
        'churchUri': '/scriptures/ot/ps',
        'numberedChapters': 0,
        'namedChapters': ['119'], # Test cases: "Lord" in all caps, sections in chapter, chapter title "Psalm 119" instead of "Psalms 119"
      },
    },
  },
  'new-testament': {
    'name': 'New Testament',
    'abbrev': 'NT',
    'churchUri': '/scriptures/nt',
    'numBooks': 2,
    'books': {
      'matthew': {
        'churchUri': '/scriptures/nt/matt',
        'numberedChapters': 0,
        'namedChapters': ['1'],
      },
      'philippians': {
        'churchUri': '/scriptures/nt/philip',
        'numberedChapters': 0,
        'namedChapters': ['4'],
      },
    },
  },
  'book-of-mormon': {
    'name': 'Book of Mormon',
    'abbrev': 'BofM',
    'churchUri': '/scriptures/bofm',
    'numBooks': 2,
    'books': {
      '1-nephi': {
        'churchUri': '/scriptures/bofm/1-ne',
        'numberedChapters': 0,
        'namedChapters': ['1', '3'],
      },
      'enos': {
        'churchUri': '/scriptures/bofm/enos',
        'numberedChapters': 0,
        'namedChapters': ['1'],
      },
      'alma': {
        'churchUri': '/scriptures/bofm/alma',
        'numberedChapters': 0,
        'namedChapters': ['17'],
      },
    },
  },
  'doctrine-and-covenants': {
    'name': 'Doctrine and Covenants',
    'abbrev': 'D&C',
    'churchUri': '/scriptures/dc-testament',
    'numBooks': 2,
    'books': {
      'sections': {
        'churchUri': '/scriptures/dc-testament/dc',
        'numberedChapters': 0,
        'namedChapters': ['1', '77', '84'],
      },
      'official-declarations': {
        'churchUri': '/scriptures/dc-testament/od',
        'numberedChapters': 0,
        'namedChapters': ['1', '2'],
      },
    },
  },
  'pearl-of-great-price': {
    'name': 'Pearl of Great Price',
    'abbrev': 'PGP',
    'churchUri': '/scriptures/pgp',
    'numBooks': 3,
    'books': {
      'moses': {
        'churchUri': '/scriptures/pgp/moses',
        'numberedChapters': 0,
        'namedChapters': ['1'],
      },
      'abraham': {
        'churchUri': '/scriptures/pgp/abr',
        'numberedChapters': 0,
        'namedChapters': ['fac-3'],
      },
      'joseph-smith-history': {
        'churchUri': '/scriptures/pgp/js-h',
        'numberedChapters': 0,
        'namedChapters': ['1'],
      },
    },
  },
}

# HTML template
with open(os.path.join(working_directory, 'template-html.html'), 'r', encoding='utf-8') as f:
  html_template = f.read()

# CSS template
with open(os.path.join(working_directory, 'template-css.css'), 'r', encoding='utf-8') as f:
  css_template = f.read()

# README template
with open(os.path.join(working_directory, 'template-readme.txt'), 'r', encoding='utf-8') as f:
  readme_template = f.read()

# MySQL SQL template
with open(os.path.join(working_directory, 'template-mysql.sql'), 'r', encoding='utf-8') as f:
  sql_mysql_template = f.read()

# SQLite SQL template
with open(os.path.join(working_directory, 'template-sqlite.sql'), 'r', encoding='utf-8') as f:
  sql_sqlite_template = f.read()
