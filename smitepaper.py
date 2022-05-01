import argparse
import logging
import datetime
import sys

from constants import (
    CSV_DEFAULT_FORMAT,
    FILEMODE_LOAD,
    FILEMODE_OVERWRITE,
    SLUGS_FILENAME,
    FILEMODE_UPDATE,
    WALLPAPERS_FILENAME,
)
from downloader import Downloader
from scraper import SlugScraper, WallpaperScraper
from utils import readlines, size

from writers import CsvWriter, WallpaperCsvWriter

date = datetime.date.today()
logging.basicConfig(
    handlers=[logging.FileHandler(filename=f"{date}.log", encoding="utf-8")],
    level=logging.INFO,
    format="%(asctime)s: %(levelname)s: %(message)s",
    datefmt="%Y.%m.%d %H:%M:%S",
)


def scrape_slugs(options):
    print("scraping slugs", options)
    slug_scraper = SlugScraper(
        CsvWriter(options.slugs_output_file),
        limit=options.limit,
        offset=options.offset,
        output_path=options.slugs_output_file,
        filemode=options.slugs_filemode,
    )
    slugs = slug_scraper.scrape()
    return slugs


def scrape(options):
    if not options.slugs:
        vars(options)["slugs"] = scrape_slugs(options)
    print("scraping wallpapers", options)
    wallpaper_scraper = WallpaperScraper(
        WallpaperCsvWriter(options.wallpapers_output_file, options.format),
        slugs=options.slugs,
        gods=options.gods,
        skins=options.skins,
        sizes=options.sizes,
        output_path=options.wallpapers_output_file,
        filemode=options.wallpapers_filemode,
    )
    wallpaper_scraper.scrape()


def download(options):
    print("downloading", options)
    # downloader = Downloader(sizes={(3840, 2160)})
    # downloader.download()


if __name__ == "__main__":
    main_parser = argparse.ArgumentParser(
        description="Smite wallpaper scraper and downloader"
    )
    subparsers = main_parser.add_subparsers(title="subcommands")

    parent_parser = argparse.ArgumentParser(add_help=False)
    slug_group = parent_parser.add_mutually_exclusive_group()
    slug_group.add_argument("-s", "--slugs", nargs="+")
    slug_group.add_argument(
        "-i",
        "--slugs-input-file",
        default=SLUGS_FILENAME,
        type=readlines,
        dest="slugs",
        help="a file containing the slugs to scrape the data from",
    )
    parent_parser.add_argument("-g", "--gods", nargs="+")
    parent_parser.add_argument("--skins", nargs="+")
    parent_parser.add_argument("--sizes", type=size, nargs="+")
    parent_parser.add_argument(
        "--format", choices=CSV_DEFAULT_FORMAT, default=CSV_DEFAULT_FORMAT, nargs="+"
    )

    slug_parent_parser = argparse.ArgumentParser(add_help=False)
    slug_parent_parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        help="the number of posts to be searched",
    )
    slug_parent_parser.add_argument(
        "--offset", type=int, default=0, help="the number of posts to skip"
    )
    # slug_parent_parser.add_argument("-o", "--output", help="path to the output file")
    slug_parent_parser.add_argument(
        "--sof",
        "--slugs-output-file",
        dest="slugs_output_file",
        default=SLUGS_FILENAME,
        help="the file to put the scraped slugs in",
    )
    slug_parent_parser.add_argument(
        "--slugs-filemode",
        choices=(FILEMODE_LOAD, FILEMODE_OVERWRITE, FILEMODE_UPDATE),
        default=FILEMODE_LOAD,
        help="whether to load and use (l), overwrite (o) or update (u) the output file if it exists",
    )

    scrape_parser = subparsers.add_parser(
        "scrape",
        help="scrape slugs and information about wallpapers",
        parents=[parent_parser, slug_parent_parser],
    )
    scrape_parser.add_argument(
        "--wallpapers-filemode",
        choices=(FILEMODE_OVERWRITE, FILEMODE_UPDATE),
        default=FILEMODE_UPDATE,
        help="whether to overwrite (o) or update (u) the output file if it exists",
    )
    scrape_parser.add_argument(
        "--wof",
        "--wallpapers-output-file",
        dest="wallpapers_output_file",
        default=WALLPAPERS_FILENAME,
    )
    scrape_parser.set_defaults(func=scrape)

    download_parser = subparsers.add_parser(
        "download",
        help="download wallpapers from the scraped data",
        parents=[parent_parser],
    )
    download_parser.add_argument(
        "-o",
        "--output",
        help="output destination",  # TODO add support for output format
    )
    download_parser.set_defaults(func=download)

    scrape_subparsers = scrape_parser.add_subparsers(title="subcommands")

    scrape_slugs_parser = scrape_subparsers.add_parser(
        "slugs",
        help="scrape slugs only",
        parents=[slug_parent_parser],
    )
    scrape_slugs_parser.set_defaults(func=scrape_slugs)

    args = main_parser.parse_args(None if sys.argv[1:] else ["--help"])
    args.func(args)
