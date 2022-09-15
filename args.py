import argparse
import sys
import warnings

from constants import (
    ALL_SIZES,
    CSV_DEFAULT_FORMAT,
    DEFAULT_WALLPAPER_OUTPUT_FILEPATH,
    FILEMODE_LOAD,
    FILEMODE_OVERWRITE,
    SLUGS_FILENAME,
    FILEMODE_UPDATE,
    WALLPAPERS_FILENAME,
)


def collect_args(scrape_func, scrape_slugs_func, download_func):
    """
    Returns parsed arguments. Callback functions must be provided for each subparser.

    :param scrape_func: function to use when the `scrape` command is used
    :param scrape_slugs_func: function to use when the `scrape slugs` command is used
    :param download_func: function to use when the `download` command is used
    :returns: parsed arguments
    """
    main_parser = argparse.ArgumentParser(
        description="Smite wallpaper scraper and downloader"
    )
    subparsers = main_parser.add_subparsers(title="subcommands")

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "--log", action="store_true", help="Log events to a file."
    )
    slug_group = parent_parser.add_mutually_exclusive_group()
    slug_group.add_argument("-s", "--slugs", nargs="+")
    slug_group.add_argument(
        "-i",
        "--slugs-input-file",
        default=SLUGS_FILENAME,
        type=readlines,
        dest="slugs",
        help="A file containing the slugs to scrape the data from.",
    )
    parent_parser.add_argument("-g", "--gods", nargs="+")
    parent_parser.add_argument("--skins", nargs="+")
    parent_parser.add_argument("--sizes", type=size, nargs="+")
    parent_parser.add_argument(
        "--output-format",
        choices=CSV_DEFAULT_FORMAT,
        default=CSV_DEFAULT_FORMAT,
        nargs="+",
    )

    slug_parent_parser = argparse.ArgumentParser(add_help=False)
    slug_parent_parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        help="The number of posts to be searched.",
    )
    slug_parent_parser.add_argument(
        "--offset", type=int, default=0, help="The number of posts to skip."
    )
    # slug_parent_parser.add_argument("-o", "--output", help="path to the output file")
    slug_parent_parser.add_argument(
        "--sof",
        "--slugs-output-file",
        dest="slugs_output_file",
        default=SLUGS_FILENAME,
        help="The file to put the scraped slugs in.",
    )
    slug_parent_parser.add_argument(
        "--slugs-filemode",
        choices=(FILEMODE_LOAD, FILEMODE_OVERWRITE, FILEMODE_UPDATE),
        default=FILEMODE_UPDATE,
        help="Whether to load and use (l), overwrite (o) or update (u) the output file if it exists.",
    )

    scrape_parser = subparsers.add_parser(
        "scrape",
        help="Scrape slugs and information about wallpapers.",
        parents=[parent_parser, slug_parent_parser],
    )
    scrape_parser.add_argument(
        "--wallpapers-filemode",
        choices=(FILEMODE_OVERWRITE, FILEMODE_UPDATE),
        default=FILEMODE_UPDATE,
        help="Whether to overwrite (o) or update (u) the output file if it exists.",
    )
    scrape_parser.add_argument(
        "--wof",
        "--wallpapers-output-file",
        dest="wallpapers_output_file",
        default=WALLPAPERS_FILENAME,
    )
    scrape_parser.set_defaults(func=scrape_func)

    download_parser = subparsers.add_parser(
        "download",
        help="Download wallpapers from the scraped data.",
        parents=[parent_parser],
    )
    download_parser.add_argument(
        "--input-file",
        default=WALLPAPERS_FILENAME,
        help="File from which to read wallpaper data.",
    )
    download_parser.add_argument(
        "--input-format",
        default=CSV_DEFAULT_FORMAT,
        dest="format",
        help="Format of the input file.",
    )
    download_parser.add_argument(
        "--output_filepath",
        type=output_filepath,
        default=DEFAULT_WALLPAPER_OUTPUT_FILEPATH,
        help="Output filepath. Supported format strings: '{god}', '{skin}', '{size}', '{extension}'",
    )
    download_parser.set_defaults(func=download_func)

    scrape_subparsers = scrape_parser.add_subparsers(title="subcommands")

    scrape_slugs_parser = scrape_subparsers.add_parser(
        "slugs",
        help="scrape slugs only",
        parents=[slug_parent_parser],
    )
    scrape_slugs_parser.set_defaults(func=scrape_slugs_func)

    args = main_parser.parse_args(None if sys.argv[1:] else ["--help"])
    return args


def size(s):
    try:
        width, height = map(int, s.split("x"))
        if (width, height) not in ALL_SIZES:
            warnings.warn(
                f"Size {width}x{height} is not common. Probably won't find anything."
            )
        return width, height
    except Exception:
        raise argparse.ArgumentTypeError(
            "Size must have the following format: 'WIDTHxHEIGHT' (eg. 1920x1080)."
        )


def output_filepath(s):
    try:
        s.format(god="god", skin="skin", size="size", extension="extension")
        return s
    except KeyError as e:
        raise argparse.ArgumentTypeError(
            f"Unsupported variable name {e.args[0]}. "
            "Output file path only supports variables 'god', 'skin', 'size', and 'extension'."
        )


def readlines(filepath):
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
            return [line.strip() for line in lines if line.strip()]
    except FileNotFoundError:
        raise argparse.ArgumentTypeError(f"File {filepath} not found.")
