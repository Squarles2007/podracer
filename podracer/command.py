import sys
import argparse
from . import _program
#from clint.textui import puts, indent, colored
import feedparser
import urllib.request
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
    # Allow --day and --night options, but not together.
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--all",
                       help = "download all episodes available in RSS feed",
                       action = "store_true")
    group.add_argument("--count",
                       "-c",
                       help = "specify the number of recent episodes to download",
                       type=int,
                       default=1)

    args = parser.parse_args(args)

    d = feedparser.parse(args.rss_url[0])
    if not args.all:
        for ep in d['entries'][:args.count]:
            split = urllib.parse.urlsplit(ep['media_content'][0]['url'])
            filename = split.path.split("/")[-1]
            urllib.request.urlretrieve(ep['media_content'][0]['url'], filename)
    elif args.all:
        for ep in d['entries']:
            split = urllib.parse.urlsplit(ep['media_content'][0]['url'])
            filename = split.path.split("/")[-1]
            urllib.request.urlretrieve(ep['media_content'][0]['url'], filename)


if __name__ == '__main__':
    main()
