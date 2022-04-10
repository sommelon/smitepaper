from constants import WALLPAPERS_FILENAME
from downloader import Downloader
from scraper import Scraper

from writers import CsvWriter


def main():
    scraper = Scraper(CsvWriter(WALLPAPERS_FILENAME))
    scraper.scrape()
    # downloader = Downloader(sizes={(3840, 2160)})
    # downloader.download()


if __name__ == "__main__":
    main()
