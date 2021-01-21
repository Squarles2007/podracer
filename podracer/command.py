import sys
import argparse
from . import _program
from clint.textui import puts, indent, colored
import feedparser
import urllib.request
import warnings
from pathvalidate import sanitize_filename

try:
    from urllib.parse import urlparse
except ImportError:
     from urlparse import urlparse

def main(args = sys.argv[1:]):
    parser = argparse.ArgumentParser(prog = _program)

    parser.add_argument("rss_url",
                        nargs=1,
                        help="URL of podcast RSS feed",
                        type=str)
    parser.add_argument("--test",
                        "-t",
                        help="Test mode: podracer will not download episodes",
                        dest='test',
                        action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--all",
                       help="download all episodes available in RSS feed",
                       action="store_const",
                       dest='count',
                       const=-1)
    group.add_argument("--count",
                       "-c",
                       help="specify the number of recent episodes to download",
                       type=int,
                       default=1)
    parser.set_defaults(test=False)
    args = parser.parse_args(args)

    # here is the actual program execution
    parsefeed(args.rss_url[0], args.count, args.test)


if __name__ == '__main__':
    main()

# pass url of RSS feed, count of recent episodes to download, or none or neg int for all, test boolean to not download


def parsefeed(url: str, count: int = -1, test: bool = False):
    # parse the feed
    d = feedparser.parse(url)
    # for all episodes set count to length of feed
    if count < 0:
        count = len(d['entries'])
    # handle requested number of episodes exceeding available
    if count > len(d['entries']):
        count = len(d['entries'])
        warnings.warn("Reguested number of episodes exceeds available downloading all:" + str(len(d['entries'])))
    # iterate episode listings and download
    for ep in d['entries'][:count]:
        # store a human readable name for file
        filename = sanitize_filename(d.feed.title + " - " + ep.itunes_episode + " - " + ep.title + ".mp3")
        # find the link with mime type audio/mpeg
        for l in ep.links:
            if l.type == 'audio/mpeg':
                puts(colored.green('Downloading: ' + filename))
                with(indent(4)):
                    puts(colored.green('From: ' + l.href))
                if not test:
                    urllib.request.urlretrieve(l.href, filename)

            else:
                continue
