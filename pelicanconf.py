from datetime import datetime
import os
from zoneinfo import ZoneInfo

AUTHOR = "Guillaume Lemaitre"
SITENAME = "FSGT 71"
SITEURL = os.getenv("GHA_SITE_URL", "")

PATH = "content"

TIMEZONE = "Europe/Paris"

DEFAULT_LANG = "fr"

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (
    ("Pelican", "https://getpelican.com/"),
    ("Python.org", "https://www.python.org/"),
    ("Jinja2", "https://palletsprojects.com/p/jinja/"),
    ("You can modify those links in your config file", "#"),
)

# Social widget
SOCIAL = (
    ("You can add links in your config file", "#"),
    ("Another social link", "#"),
)

DEFAULT_PAGINATION = 5
PAGINATION_PATTERNS = (
    (1, "{url}", "{save_as}"),
    (2, "{base_name}/page/{number}/", "{base_name}/page/{number}/index.html"),
)

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

# The articles are related to the news feed.
ARTICLE_PATHS = ["news"]
# to avoid conflict with the pages, we use the date in the URL.
ARTICLE_URL = "{date:%Y}/{date:%m}/{date:%d}/{slug}.html"
ARTICLE_SAVE_AS = "{date:%Y}/{date:%m}/{date:%d}/{slug}.html"
DEFAULT_CATEGORY = "news"

# Pages are defined for the general website
PAGE_PATHS = ["pages"]

MARKDOWN = {
    "extension_configs": {
        "markdown.extensions.attr_list": {},
        "markdown.extensions.tables": {},
    }
}

BUILD_TIME = datetime.now(tz=ZoneInfo(TIMEZONE))
