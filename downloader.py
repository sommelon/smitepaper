import csv
from pathlib import Path
from typing import Iterable, Tuple
import shutil
from constants import ALL_SIZES
import requests

from utils import Wallpaper, is_url_valid


class Downloader:
    def __init__(
        self,
        source_path="wallpapers.csv",
        destination_path="./downloads",
        sizes: Iterable[Tuple] = ALL_SIZES,
    ):
        self.source_path = Path(source_path)
        destination_path = Path(destination_path)
        destination_path.mkdir(parents=True, exist_ok=True)
        self.destination_path = destination_path
        for size in sizes:
            if size not in ALL_SIZES:
                raise ValueError(f"The size {size} is not supported.")
        self.sizes = sizes
        self._load_data()

    def _load_data(self):
        self.wallpapers = []
        with open(self.source_path) as f:
            reader = csv.reader(f)
            for row in reader:
                wallpaper = Wallpaper(row[1], row[2], row[3], row[0], row[4])
                if wallpaper.size in self.sizes:
                    self.wallpapers.append(wallpaper)

    def download(self):
        for wallpaper in self.wallpapers:
            filename = self.destination_path / wallpaper.get_filename()
            if filename.exists():
                print(f"File {filename} already exists. Skipping.")
                continue
            if is_url_valid(wallpaper.image_link):
                self._save_wallpaper(wallpaper.image_link, filename)
                print(f"Saved skin {wallpaper.name} to {filename}.")
            else:
                print(f"Skin {wallpaper.name} doesn't have a valid link. Skipping.")

    def _save_wallpaper(self, url, local_filename):
        with requests.get(url, stream=True) as response:
            with open(local_filename, "wb") as f:
                shutil.copyfileobj(response.raw, f)

        return local_filename
