import argparse
import logging
import datetime

from constants import ALL_SIZES, SLUGS_FILENAME, WALLPAPERS_FILENAME
from downloader import Downloader
from scraper import WallpaperScraper
from utils import size

from writers import CsvWriter

time = datetime.date.today()
logging.basicConfig(filename=f"{time}.log", level=logging.INFO)


def main(options):
    scrape(options)
    download(options)


def scrape(options):
    print("scraping", options)
    # slug_scraper = SlugScraper()
    # slugs = slug_scraper.scrape()
    # wallpaper_scraper = WallpaperScraper(CsvWriter(WALLPAPERS_FILENAME), slugs=slugs)
    # wallpaper_scraper.scrape()


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
    slug_group.add_argument("-s", "--slug", nargs="+")
    slug_group.add_argument("-i", "--input-file", default=SLUGS_FILENAME)
    parent_parser.add_argument("-g", "--god", nargs="+")
    parent_parser.add_argument("--skin", nargs="+")
    parent_parser.add_argument("--size", type=size, nargs="+")
    parent_parser.add_argument("-o", "--output-file", default=SLUGS_FILENAME)

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
