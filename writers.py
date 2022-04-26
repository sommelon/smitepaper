import csv
from typing import List

from constants import CSV_DEFAULT_FORMAT
from utils import Wallpaper


class BaseWriter:
    def write(self, data, **kwargs):
        raise NotImplementedError()


class Printer(BaseWriter):
    def write(self, data, **kwargs):
        print(data)


class CsvWriter(BaseWriter):
    def __init__(self, path):
        self.path = path

    def write(self, data, **kwargs):
        mode = kwargs.get("mode", "w")
        with open(self.path, mode, encoding="utf-8") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerows(data)


class WallpaperCsvWriter(CsvWriter):
    def __init__(self, path, format=CSV_DEFAULT_FORMAT):
        super().__init__(path)
        self.format = format

    def write(self, wallpapers: List[Wallpaper], **kwargs):
        mode = kwargs.get("mode", "w")
        with open(self.path, mode, encoding="utf-8") as f:
            writer = csv.writer(f, lineterminator="\n")
            for wallpaper in wallpapers:
                writer.writerow(wallpaper.to_list(self.format))
