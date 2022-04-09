import re
import sys
import json
import requests
from parsel import Selector
import os.path
import csv

from utils import Wallpaper, get_god_name
from writers import BaseWriter, CsvWriter


POSTS_URL = "https://cms.smitegame.com/wp-json/smite-api/get-posts/1"
POST_URL = "https://cms.smitegame.com/wp-json/smite-api/get-post/1"
SLUGS_FILENAME = "slugs.txt"
WALLPAPERS_FILENAME = "wallpapers.csv"


def main():
    scraper = Scraper(CsvWriter(WALLPAPERS_FILENAME))
    scraper.scrape()


class Scraper:
    def __init__(self, writer: BaseWriter):
        self.writer = writer
        self.scraped_skins = set()
        if os.path.isfile(WALLPAPERS_FILENAME):
            with open(WALLPAPERS_FILENAME, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    self.scraped_skins.add((row[1], row[2] if row[2] else None))

    def scrape(self, limit=1000, offset=0):
        slugs = self._get_slugs(limit, offset)
        self._scrape_slugs(slugs)

    def _get_slugs(self, limit=1000, offset=0):
        if os.path.isfile(SLUGS_FILENAME):
            # retrieve slugs from cache
            with open(SLUGS_FILENAME, "r") as f:
                return f.read().splitlines()

        response = requests.get(
            POSTS_URL,
            dict(
                per_page=limit,
                offset=offset,
            ),
        )
        if not response.ok:
            response.raise_for_status()

        data = json.loads(response.text)
        update_notes = [
            d for d in data if "update notes" in d["real_categories"].lower()
        ]
        slugs = list(reversed([d["slug"] for d in update_notes]))

        # cache slugs
        with open(SLUGS_FILENAME, "a") as f:
            f.write("\n".join(slugs))
        return slugs

    def _scrape_slugs(self, slugs):
        for slug in slugs:
            url = POST_URL + f"?slug={slug}"
            try:
                wallpapers = self._get_wallpapers(url)
                data = []
                for wallpaper in wallpapers:
                    if (wallpaper.name, wallpaper.image_link) in self.scraped_skins:
                        continue
                    data.append(
                        [get_god_name(wallpaper.name)] + wallpaper.to_csv() + [slug]
                    )
                    self.scraped_skins.add((wallpaper.name, wallpaper.image_link))
                self.writer.write(data, mode="a")
            except Exception as e:
                print("Error on url " + url + ": ", file=sys.stderr)
                raise e

    def _get_wallpapers(self, url):
        print(url)
        response = requests.get(url)
        if not response.ok:
            response.raise_for_status()

        data = json.loads(response.text)
        selector = Selector(data["content"])
        wallpapers = []
        wallpapers.extend(self._get_new_god_wallpapers(selector))
        wallpapers.extend(self._get_card_wallpapers(selector))
        return wallpapers

    def _get_new_god_wallpapers(self, selector):
        wallpapers = []
        god_name = selector.xpath("//div[@class='new-god']//h3/text()").get()
        recolor_name = selector.xpath(
            "//div[@class='new-god--recolor']//text()[last()]"
        ).get()
        new_god_wallpapers = selector.xpath("//div[@class='new-god--wallpapers']")

        if god_name:
            basic_skin_anchors = new_god_wallpapers[0].xpath(".//a")
            wallpapers.extend(
                self._get_wallpapers_from_anchors(god_name, basic_skin_anchors)
            )
        if recolor_name:
            recolor_name = (
                re.sub("\\W", " ", recolor_name).replace("Recolor", "").strip()
            )
            for wallpaper in new_god_wallpapers[1:]:
                recolor_wallpaper_anchors = wallpaper.xpath(".//a")
                wallpapers.extend(
                    self._get_wallpapers_from_anchors(
                        recolor_name, recolor_wallpaper_anchors
                    )
                )
        return wallpapers

    def _get_card_wallpapers(self, selector):
        wallpapers = []
        cards = selector.xpath("//div[@class='god-skin--card']")

        for card in cards:
            wallpaper_anchors = card.xpath("div[@class='god-skins--wallpapers']//a")
            name = card.xpath("p[@class='name']/text()").get()
            if name:
                wallpapers.extend(
                    self._get_wallpapers_from_anchors(name, wallpaper_anchors)
                )
        return wallpapers

    def _get_wallpapers_from_anchors(self, name, anchors_selector):
        print("Getting wallpapers for card " + str(name))
        wallpapers = []
        for anchor in anchors_selector:
            image_link = anchor.xpath("@href").get()
            if not int(anchor.xpath("contains(@href,'http')").get()):
                image_link = None
            size = anchor.xpath("text()").get()
            size = re.findall("\\d+", size)
            size = tuple([int(e) for e in size])
            wallpaper = Wallpaper(name, image_link, size)
            wallpapers.append(wallpaper)
        return wallpapers


if __name__ == "__main__":
    main()
