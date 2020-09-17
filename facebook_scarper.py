import csv
import locale
import logging
import sys
from typing import Iterator, Optional, Tuple, Union
from facebook_scraper import FacebookScraper
from typing import Any, Callable, Dict, Iterable, Set, Tuple
from requests import Response
from requests_html import Element


FB_MOBILE_BASE_URL = 'https://m.facebook.com/'

DEFAULT_REQUESTS_TIMEOUT = 5
DEFAULT_PAGE_LIMIT = 10

URL = str
Options = Set[str]
Post = Dict[str, Any]
RequestFunction = Callable[[URL], Response]
RawPage = Element
RawPost = Element
Page = Iterable[RawPost]
Credentials = Tuple[str, str]

_scraper = FacebookScraper()

def get_posts(
    account: Optional[str] = None,
    group: Union[str, int, None] = None,
    credentials: Optional[Credentials] = None,
    **kwargs,
) -> Iterator[Post]:
    valid_args = sum(arg is not None for arg in (account, group))

    if valid_args != 1:
        raise ValueError("You need to specify either account or group")

    _scraper.requests_kwargs['timeout'] = kwargs.pop('timeout', DEFAULT_REQUESTS_TIMEOUT)

    options = kwargs.setdefault('options', set())

    if 'pages' in kwargs:
        kwargs['page_limit'] = kwargs.pop('pages')

    extra_info = kwargs.pop('extra_info', False)
    if extra_info:
        options.add('reactions')
    if kwargs.pop('youtube_dl', False):
        options.add('youtube_dl')

    if credentials is not None:
        _scraper.login(*credentials)

    if account is not None:
        return _scraper.get_posts(account, **kwargs)

    elif group is not None:
        return _scraper.get_group_posts(group, **kwargs)


def write_posts_to_csv(
    account: Optional[str] = None,
    group: Union[str, int, None] = None,
    filename: str = None,
    encoding: str = None,
    **kwargs,
):
    list_of_posts = list(get_posts(account=account, group=group, **kwargs))

    if not list_of_posts:
        print("Couldn't get any posts.", file=sys.stderr)
        return

    keys = list_of_posts[0].keys()

    if filename is None:
        filename = str(account or group) + "_posts.csv"

    if encoding is None:
        encoding = locale.getpreferredencoding()

    with open(filename, 'w', encoding="utf-8") as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(list_of_posts)


def enable_logging(level=logging.INFO):
    handler = logging.StreamHandler()
    handler.setLevel(level)

    logger.addHandler(handler)
    logger.setLevel(level)


# Disable logging by default
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

#####################################################################################################################

for post in get_posts(group='57812275694', pages=500):
    print(post)

write_posts_to_csv(group="57812275694")

