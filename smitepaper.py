import logging
import datetime
from args import collect_args

from downloader import Downloader
from scraper import SlugScraper, WallpaperScraper


from writers import CsvWriter, WallpaperCsvWriter


def scrape_slugs(options):
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
    downloader = Downloader(
        input_file=options.input_file,
        input_format=options.format,
        slugs=options.slugs,
        gods=options.gods,
        skins=options.skins,
        sizes=options.sizes,
        output_filepath=options.output_filepath,
    )
    downloader.download()


if __name__ == "__main__":
    args = collect_args(scrape, scrape_slugs, download)
    if args.log:
        # Setup logging
        date = datetime.date.today()
        logging.basicConfig(
            handlers=[logging.FileHandler(filename=f"{date}.log", encoding="utf-8")],
            level=logging.INFO,
            format="%(asctime)s: %(levelname)s: %(message)s",
            datefmt="%Y.%m.%d %H:%M:%S",
        )
    args.func(args)
