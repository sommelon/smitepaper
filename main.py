from constants import WALLPAPERS_FILENAME
from scraper import Scraper

from writers import CsvWriter


def main():
    scraper = Scraper(CsvWriter(WALLPAPERS_FILENAME))
    scraper.scrape()


if __name__ == "__main__":
    main()
