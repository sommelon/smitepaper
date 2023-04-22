import logging
import re
import json
from typing import List
from constants import (
    FILEMODE_LOAD,
    FILEMODE_OVERWRITE,
    SLUGS_FILENAME,
    FILEMODE_UPDATE,
    WALLPAPERS_FILENAME,
)
import requests
from parsel import Selector
import os.path
import csv
from tqdm import tqdm

from utils import Wallpaper, get_god_name, is_url_valid
from writers import BaseWriter, CsvWriter, WallpaperCsvWriter

MULTIPLE_POSTS_URL = "https://cms.smitegame.com/wp-json/smite-api/get-posts/1"
SINGLE_POST_URL = "https://cms.smitegame.com/wp-json/smite-api/get-post/1"


class SlugScraper:
    def __init__(
        self,
        writer: BaseWriter = CsvWriter,
        limit=1000,
        offset=0,
        output_path=SLUGS_FILENAME,
        filemode=FILEMODE_LOAD,
        # TODO: Add option to specify date range
    ):
        self.writer = writer
        self.limit = limit
        self.offset = offset
        self.output_path = output_path
        self.filemode = filemode

    def scrape(self):
        if os.path.isfile(self.output_path):
            if self.filemode == FILEMODE_LOAD:
                # retrieve slugs from an existing file
                with open(self.output_path, "r") as f:
                    print(f"Loading slugs from file {self.output_path}.")
                    reader = csv.reader(f)
                    slugs = [row[1] for row in reader if row]
                    return slugs

        response = requests.get(
            MULTIPLE_POSTS_URL,
            dict(
                per_page=self.limit,
                offset=self.offset,
            ),
        )
        response.raise_for_status()

        data = json.loads(response.text)
        update_notes = [
            d for d in data if "update notes" in d["real_categories"].lower()
        ]
        slugs_with_timestamps = [(d["timestamp"], d["slug"]) for d in update_notes]
        if self.filemode == FILEMODE_UPDATE:
            # merge old slugs with the new ones
            with open(self.output_path, "r") as f:
                reader = csv.reader(f)
                existing_slugs_with_timestamps = [tuple(row) for row in reader if row]
                slugs_with_timestamps.extend(existing_slugs_with_timestamps)

        slugs_with_timestamps = list(sorted(set(slugs_with_timestamps)))
        self.writer.write(slugs_with_timestamps)
        slugs_without_timestamps = [slug[1] for slug in slugs_with_timestamps]
        return slugs_without_timestamps


class WallpaperScraper:
    def __init__(
        self,
        writer: BaseWriter = WallpaperCsvWriter,
        slugs=None,
        gods=None,
        skins=None,
        sizes=None,
        output_path=WALLPAPERS_FILENAME,
        filemode=FILEMODE_UPDATE,
    ):
        self.writer = writer
        self.slugs = slugs or []
        self.gods = gods or []
        self.skins = skins or []
        self.sizes = sizes or []
        self.output_path = output_path
        self.filemode = filemode
        self.scraped_skins = set()
        self.failed_urls = set()

        if filemode != FILEMODE_OVERWRITE and os.path.isfile(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.scraped_skins.add(
                        (
                            row.get("skin") or None,
                            row.get("link") or None,
                            row.get("size") or None,
                        )
                    )

    def scrape(self):
        all_wallpapers = []
        for slug in tqdm(self.slugs):
            url, params = SINGLE_POST_URL, {"slug": slug}
            try:
                wallpapers = self._get_wallpapers(url, params)
                wallpapers_to_save = []
                for wallpaper in wallpapers:
                    if (
                        wallpaper.name,
                        wallpaper.image_link,
                        wallpaper.size_to_text(),
                    ) in self.scraped_skins:
                        logging.info(
                            f"Wallpaper {wallpaper} already scraped, skipping."
                        )
                        continue

                    god_name = get_god_name(wallpaper.name)
                    if self.gods and god_name not in self.gods:
                        continue

                    wallpaper.god = god_name
                    wallpaper.slug = slug
                    self.scraped_skins.add(
                        (wallpaper.name, wallpaper.image_link, wallpaper.size_to_text())
                    )
                    wallpapers_to_save.append(wallpaper)

                filemode = "a" if self.filemode == FILEMODE_UPDATE else "w"
                self.writer.write(wallpapers_to_save, mode=filemode)
                all_wallpapers.extend(wallpapers_to_save)
            except Exception:
                self.failed_urls.add(url)
                logging.exception("Error on url " + url)
        return all_wallpapers

    def _get_wallpapers(self, url, params) -> List[Wallpaper]:
        print(url, params)
        response = requests.get(url, params)
        response.raise_for_status()

        data = json.loads(response.text)
        selector = Selector(data["content"])
        wallpapers = []
        wallpapers.extend(self._get_new_god_wallpapers(selector))
        wallpapers.extend(self._get_card_wallpapers(selector))
        return wallpapers

    def _get_new_god_wallpapers(self, selector):
        wallpapers = []
        god_name = selector.xpath(".//div[@class='new-god']//h3/text()").get()
        recolor_name = selector.xpath(
            ".//div[@class='new-god--recolor']//text()[last()]"
        ).get()
        new_god_wallpapers = selector.xpath(".//div[@class='new-god--wallpapers']")
        new_god_background_image_link = None
        if not new_god_wallpapers:
            element = selector.xpath(".//div[@class='new-god']")
            style = element.attrib["style"]
            new_god_background_image_link = style.split("'")[1]

        if god_name:
            try:
                basic_skin_anchors = new_god_wallpapers[0].xpath(".//a")
                wallpapers.extend(
                    self._get_wallpapers_from_anchors(god_name, basic_skin_anchors)
                )
            except IndexError:
                wallpapers.append(
                    Wallpaper(
                        god_name,
                        new_god_background_image_link,
                        None,  # To get the size, we would need to download the image
                    )
                )
        if recolor_name:
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
        cards = selector.xpath(".//div[@class='god-skin--card']")

        for card in cards:
            wallpaper_anchors = card.xpath("div[@class='god-skins--wallpapers']//a")
            name = card.xpath("p[@class='name']/text()").get()
            if name:
                wallpapers.extend(
                    self._get_wallpapers_from_anchors(name, wallpaper_anchors)
                )
        return wallpapers

    def _get_wallpapers_from_anchors(self, name, anchors_selector):
        if self.skins and not [skin for skin in self.skins if skin in name]:
            return []

        print(f"Getting wallpapers for card {name}")
        wallpapers = []
        for anchor in anchors_selector:
            image_link = anchor.xpath("@href").get()
            if not is_url_valid(image_link):
                logging.info(f"Skin {name}: URL {image_link} not valid.")
                image_link = None
            size = anchor.xpath("text()").get()
            size = re.findall("\\d+", size)
            size = tuple(int(e) for e in size)
            if not self.sizes or size in self.sizes:
                wallpaper = Wallpaper(name, image_link, size)
                wallpapers.append(wallpaper)
        return wallpapers
