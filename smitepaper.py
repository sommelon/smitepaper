import argparse

from constants import WALLPAPERS_FILENAME
from downloader import Downloader
from scraper import Scraper

from writers import CsvWriter


def main(options):
    scrape(options)
    download(options)


def scrape(options):
    print("scraping", options)
    # scraper = Scraper(CsvWriter(WALLPAPERS_FILENAME))
    # scraper.scrape()


def download(options):
    print("downloading", options)
    # downloader = Downloader(sizes={(3840, 2160)})
    # downloader.download()


if __name__ == "__main__":
    main_parser = argparse.ArgumentParser(description="")
    main_parser.set_defaults(func=main)
    subparsers = main_parser.add_subparsers(title="subcommands")
    parent_parser = argparse.ArgumentParser(add_help=False)
    slug_group = parent_parser.add_mutually_exclusive_group()
    slug_group.add_argument("-s", "--slugs", nargs="+")
    slug_group.add_argument("-i", "--input-file", default="slugs.txt")
    parent_parser.add_argument("-g", "--god")
    parent_parser.add_argument("--skin")
    parent_parser.add_argument("--size")
    parent_parser.add_argument("-o", "--output-file", default="slugs.txt")

    scrape_parser = subparsers.add_parser(
        "scrape",
        help="Scrape information about wallpapers.",
        parents=[parent_parser],
    )
    scrape_parser.add_argument(
        "-f", "--format", choices=["god", "skin", "link", "size", "slug"], nargs="+"
    )
    scrape_parser.set_defaults(func=scrape)

    download_parser = subparsers.add_parser(
        "download",
        help="Download wallpapers from the scraped data.",
        parents=[parent_parser],
    )
    download_parser.set_defaults(func=download)

    args = main_parser.parse_args()
    args.func(args)
