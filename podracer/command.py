import sys
import argparse
from . import _program
from clint.textui import puts, indent, colored
import feedparser
import urllib.request
import warnings
from pathvalidate import replace_symbol
import eyed3
from mimetypes import guess_type
import os
from datetime import datetime

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
    parser.add_argument("--pretty",
                        "-P",
                        help="Download Album Art and insert into mp3",
                        dest='pretty',
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
                       type=int,)
    parser.set_defaults(test=False, pretty=False, count=1)
    args = parser.parse_args(args)

    # here is the actual program execution
    parsefeed(args.rss_url[0], args.count, args.test, args.pretty)


if __name__ == '__main__':
    main()

# pass url of RSS feed, count of recent episodes to download, or none or neg int for all, test boolean to not download


def parsefeed(url: str, count: int = -1, test: bool = False, pretty: bool = False):
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
    cover_url = None
    cover_art_filenames = []
    for ep in d['entries'][:count]:
        # store a human readable name for file
        if 'ep.itunes_episode' in locals():
            filename = replace_symbol(d.feed.title + " - " + ep.itunes_episode + " - " + ep.title + ".mp3", replacement_text='-')
        else:
            pub_date = datetime.strptime(ep.published, "%a, %d %b %Y %H:%M:%S %z")
            filename = replace_symbol(d.feed.title + " - " + pub_date.strftime("%Y-%m-%d") + " - " + ep.title + ".mp3",
                                      replacement_text='-')
        # find the link with mime type audio/mp3

        for l in ep.links:
            if l.type == 'audio/mpeg':
                puts(colored.green('Downloading: ' + filename))
                with(indent(4)):
                    puts(colored.green('From: ' + l.href))
                if not test:
                    urllib.request.urlretrieve(l.href, filename)
            else:
                continue

        if pretty:
            #if no cover image stored yet or if coverart is not the same as last episode
            mp3 = eyed3.load(filename)
            if (mp3.tag == None):
                mp3.initTag()
            if (cover_url is None) or (cover_url is not ep.image.href):
                cover_url = ep.image.href
                puts(colored.green('Downloading: ' + cover_url))
                split = urllib.parse.urlsplit(cover_url)
                artname = split.path.split("/")[-1]
                urllib.request.urlretrieve(ep.image.href, artname)
                if artname not in cover_art_filenames:
                    cover_art_filenames.append(artname)
            mime = guess_type(artname)
            if mp3.tag.header.major_version == 2 and mp3.tag.header.minor_version == 2:
                print('eyeD3 --to-v2.3 ' + '"' + filename + '"')
                os.system('eyeD3 --to-v2.3 ' + '"' + filename + '"')
                mp3 = eyed3.load(filename)
            if mime[0] is not None:
                mp3.tag.images.set(3, open(artname,'rb').read(), mime[0])
                mp3.tag.save()
    for f in cover_art_filenames:
        os.remove(f)




