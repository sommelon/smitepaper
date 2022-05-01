import csv
from tqdm import tqdm
from pathlib import Path
import logging
from typing import List
from constants import CSV_DEFAULT_FORMAT, DEFAULT_WALLPAPER_OUTPUT_FILEPATH
import requests
from utils import Wallpaper, is_url_valid


class Downloader:
    def __init__(
        self,
        input_file="wallpapers.csv",
        input_format=CSV_DEFAULT_FORMAT,
        output_filepath=DEFAULT_WALLPAPER_OUTPUT_FILEPATH,
        slugs=None,
        gods=None,
        skins=None,
        sizes=None,
    ):
        self.input_file = Path(input_file)
        self.output_filepath = output_filepath
        # for size in sizes:
        #     if size not in ALL_SIZES:
        #         raise ValueError(f"The size {size} is not supported.")
        self.slugs = slugs or []
        self.gods = gods or []
        self.skins = skins or []
        self.sizes = sizes or []
        self.input_format = input_format
        self.wallpapers: List[Wallpaper] = self._load_wallpapers()
        self.wallpapers = self._filter_wallpapers()

    def _load_wallpapers(self):
        wallpapers = []
        with open(self.input_file) as f:
            reader = csv.reader(f)
            skin_idx, link_idx, size_idx, god_idx, slug_idx = (
                self.input_format.index("skin"),
                self.input_format.index("link"),
                self.input_format.index("size"),
                self.input_format.index("god"),
                self.input_format.index("slug"),
            )
            for row in reader:
                wallpaper = Wallpaper(
                    row[skin_idx] if row[skin_idx] else None,
                    row[link_idx] if row[link_idx] else None,
                    row[size_idx] if row[size_idx] else None,
                    row[god_idx] if row[god_idx] else None,
                    row[slug_idx] if row[slug_idx] else None,
                )
                wallpapers.append(wallpaper)
        return wallpapers

    def _filter_wallpapers(self):
        wallpapers = self.wallpapers
        if self.slugs:
            wallpapers = filter(lambda w: w.slug in self.slugs, wallpapers)
        if self.gods:
            wallpapers = filter(lambda w: w.god in self.gods, wallpapers)
        if self.skins:
            wallpapers = filter(lambda w: w.name in self.skins, wallpapers)
        if self.sizes:
            wallpapers = filter(lambda w: w.size in self.sizes, wallpapers)
        return list(wallpapers)

    def download(self):
        for wallpaper in tqdm(self.wallpapers):
            filepath = wallpaper.get_filepath(self.output_filepath)
            filepath = Path(filepath)
            parent_dir = filepath.parents[0] if filepath.parents else filepath
            parent_dir.mkdir(parents=True, exist_ok=True)
            if filepath.exists():
                logging.info(f"File {filepath} already exists. Skipping.")
                continue

            if is_url_valid(wallpaper.image_link):
                print(f"Downloading wallpaper {wallpaper}.")
                self._download_file(wallpaper.image_link, filepath)
                logging.info(f"Saved skin {wallpaper.name} to {filepath}.")
            else:
                logging.info(
                    f"Skin {wallpaper.name} doesn't have a valid link '{wallpaper.image_link}'. Skipping."
                )

    def _download_file(self, url, filepath):
        with requests.get(url, stream=True) as response:
            with open(filepath, "wb") as f:
                for data in response.iter_content(1024):
                    f.write(data)
                # shutil.copyfileobj(response.raw, f)

        return filepath
