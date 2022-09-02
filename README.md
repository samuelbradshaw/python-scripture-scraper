# Python Scripture Scraper

This tool provides a way to download scripture content and metadata from [ChurchofJesusChrist.org](https://www.churchofjesuschrist.org/?lang=eng). Content is pulled from public-facing pages and can be output to several formats, including JSON, HTML, Markdown, plain text, CSV, TSV, SQL (MySQL), and SQL (SQLite).

The Python Scripture Scraper is licensed under the [MIT License](https://github.com/samuelbradshaw/python-scripture-scraper/blob/main/LICENSE). Scripture content downloaded by the Python Scripture Scraper using default settings is in public domain (see the Legal Q&A section below).


## Sample data

Sample data downloaded by the Python Scripture Scraper can be found in the `sample` folder in this repository. You are welcome to copy and use the sample data, or run the script yourself, following the instructions below. (Running the script yourself will allow you to adjust several parameters.)


## Running the script

1. Verify that Python 3 is installed ([installing Python with venv](https://gist.github.com/samuelbradshaw/932d48ef1eff07e288e25e4355dbce5d) is recommended):

```
python3 -V
```

2. Download the Python Scripture Scraper.

3. In Terminal, go to the `python-scripture-scraper` directory:

```
cd /path/to/python-scripture-scraper
```

4. Install dependencies:

```
pip3 install -r requirements.txt
```

5. Configure any parameters you’d like to set in `resources/config.py`.

6. Run the Python Scripture Scraper:

```
python3 scrape.py
```

Content will be downloaded to a folder called `_output`. Any previously-downloaded content in the `_output` folder will be overwritten when you run the script.


### Configuration parameters

For the full list of configuration paramaters, see [resources/config.py](https://github.com/samuelbradshaw/python-scripture-scraper/blob/main/resources/config.py)

## Legal Q&A

If you plan to distribute scraped content publicly or use it commercially, you may want to consult with a legal professional; however, the information below might be helpful for personal projects.


### Is scripture content copyrighted?

The complete text of the standard works of The Church of Jesus Christ of Latter-day Saints in English is in [public domain](https://en.wikipedia.org/wiki/Public_domain) in the United States, except for Official Declaration 2, which was first published in 1978. Public domain content is not subject to copyright, and can be used freely for any purpose.

The following content is in public domain, because it was first published more than 95 years ago:

- Old Testament (English) – King James Version, first published in 1611.
- New Testament (English) – King James Version, first published in 1611.
- Book of Mormon (English) – first published in 1830.
- Doctrine and Covenants (English) – first published in 1835, with occasional additions and removals, up through Section 138 (1918) and Official Declaration 1 (1890).
- Pearl of Great Price (English) – first published in 1851, with occasional additions and removals.

The following content is **not** in public domain, and requires [permission from the Church](https://permissions.churchofjesuschrist.org) before it can be copied for anything other than personal or Church use:

- Official Declaration 2 (1978).
- Scripture study helps, including footnotes, chapter summaries, indexes, and other reference materials first published with the Church’s 1979/1981 edition of the scriptures.
- Scripture study helps that have been added since 1981.
- Translations of the scriptures first published within the last 95 years (most translations currently in use are still under copyright).
- Audio recordings of the scriptures.
- Scripture cover artwork.

By default, the Python Scripture Scraper will not download copyrighted content. A configuration setting to include copyrighted content is available, but should be used at your own risk, and is not intended for public or commercial use.


### Is the most recent edition of the scriptures in public domain?

In the United States, copyright protections are available for “derivitive works,” which include substantial revisions or translations of an earlier work.

Section headers and other study helps added in recent editions of the scriptures qualify for their own copyright protection. How content is organized and structured in the printed book and on the Church website may also be copyrightable. However, the main scripture text has not changed significantly in the past 95 years.

In order to qualify for copyright, a newly-published work must be [original and creative](https://copyright.uslegal.com/enumerated-categories-of-copyrightable-works/creativity-requirement/). For example, these types of changes generally can’t qualify for copyright protection on their own:

- Punctuation changes, modernizing spelling, and fixing typos (the changes aren’t creative).
- Changes that bring the work closer to its original manuscript (the changes aren’t original).
- Adding a table of contents (the layout may be protectable, but the list of books isn’t creative).

The most recent major edition of the English scriptures was published in 2013. A summary of the changes can be found here: [Summary of Approved Adjustments for the 2013 Edition of the Scriptures](https://www.churchofjesuschrist.org/bc/content/shared/content/english/pdf/scriptures/approved-adjustments_eng.pdf) (PDF).

Based on the above, the main scripture text in the latest English edition of the standard works is in public domain, inheriting from the main English scripture text in previous editions.


### Is it legal to scrape content from a website?

Generally, courts in the United States have found web scraping of publicly-available web pages to be legal, but various factors are taken into consideration:

- Is the data publicly available (can anyone access it)?
- Is the data easy to access (or does it require digging in source code for an API)?
- Does accessing the data require signing in?
- Is the data sensitive (personally identifiable information)?
- Is the data copyrighted?

The Church of Jesus Christ of Latter-day Saints provides a lot of content at [ChurchofJesusChrist.org](https://www.churchofjesuschrist.org/?lang=eng) for Church members and others to use. However, the Church does not have unlimited resources, and the Church website is primarily designed to be used by humans (rather than scripts). Please be respectful in how you use this tool, to avoid overloading Church servers with too many or too frequent server requests. You will also want to avoid running the script during peak traffic times, such as Sundays.
