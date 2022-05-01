import argparse
from functools import lru_cache
import logging
import warnings
from constants import ALL_SIZES, GODS_FILENAME
import requests
from requests.exceptions import InvalidURL, MissingSchema
import re

with open(GODS_FILENAME, "r") as f:
    gods = f.read().splitlines()


def valid_input(message, choices=("",)):
    answer = input(message)
    while answer not in choices:
        answer = input(message)
    return answer


def i(string):
    """Return a pattern with the IGNORECASE flag set"""
    return re.compile(string, re.IGNORECASE)


name_map = {
    i("AMC"): "Ah Muzen Cab",
    i("AhMuzen Cab"): "Ah Muzen Cab",
    i("Isis"): "Eset",
    i("Chang’e"): "Chang'e",
    i("Sun Wukon$"): "Sun Wukong",
    i("Sun Wukongg"): "Sun Wukong",
    i("Crimson Queen"): "Crimson Queen Hera",
    i("Rightful Heir"): "Rightful Heir Horus",
    i("Withering Bloom"): "Withering Bloom Persephone",
    i("Healing Water"): "Healing Water Yemoja",
    i("Night Watch"): "Night Watch Heimdallr",
    i("Rising Hero"): "Rising Hero Mulan",
    i("Wukong"): "Sun Wukong",
    i("Khumbakarna"): "Kumbhakarna",
    i("Earl Wubert"): "Sun Wukong Earl Wubert",
    i("Neith’s Biggest Fan Zhong Kui"): "Zhong Kui",
    i("Morrigan"): "The Morrigan",
    i("Recolor – Supreme"): "Recolor – Supreme Olorun",
}


def word_pattern(w):
    # Use a regex with word boundaries to prevent matching gods like Ravana with Ra
    return re.compile(r"\b({0})\b".format(w), flags=re.IGNORECASE)


@lru_cache()
def get_god_name(skin_name):

    for pattern, replacement in name_map.items():
        skin_name, n = pattern.subn(replacement, skin_name)
        if n:
            break

    for god in gods:
        if word_pattern(god).search(skin_name):
            logging.info(f"Guessed god {god} from skin {skin_name}")
            return god
    return _ask_for_god_name(skin_name)


@lru_cache()  # Use a separate cache so we don't ask for the same skin name multiple times.
def _ask_for_god_name(skin_name):
    # TODO: Add file caching
    god = input(
        f"Couldn't find god name for skin {skin_name}. Enter the god name or skip by pressing enter: "
    )
    logging.info(f"Couldn't guess god from skin {skin_name}. User entered: {god}.")
    return god if god else None


def is_url_valid(url):
    req = requests.PreparedRequest()
    try:
        req.prepare_url(url, None)
    except (MissingSchema, InvalidURL):
        return False
    return True


def size(s):
    try:
        width, height = map(int, s.split("x"))
        if (width, height) not in ALL_SIZES:
            warnings.warn("This size is not common. Probably won't find anything.")
        return width, height
    except Exception:
        raise argparse.ArgumentTypeError(
            "Size must have the following format: 'WIDTHxHEIGHT' (eg. 1920x1080)."
        )


def readlines(filepath):
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
            return [line.strip() for line in lines if line.strip()]
    except FileNotFoundError:
        raise argparse.ArgumentTypeError(f"File {filepath} not found.")


class Wallpaper:
    SIZE_DELIMITER = "x"

    def __init__(self, name, image_link, size, god=None, slug=None):
        self.name = name
        self.image_link = image_link
        if isinstance(size, str):
            if Wallpaper.SIZE_DELIMITER not in size:
                raise ValueError(
                    f"Size {size} doesn't contain {Wallpaper.SIZE_DELIMITER}",
                )
            size = size.split(Wallpaper.SIZE_DELIMITER)
            size = tuple(map(int, size))
        self.size = size
        self.god = god
        self.slug = slug

    def size_to_text(self):
        return (
            f"{self.size[0]}{Wallpaper.SIZE_DELIMITER}{self.size[1]}"
            if self.size
            else None
        )

    def to_list(self, format):
        format_map = {
            "god": self.god,
            "skin": self.name,
            "link": self.image_link,
            "size": self.size_to_text(),
            "slug": self.slug,
        }

        return [format_map[f] for f in format if f in format_map]

    def get_filename(self):
        god = self.god or ""
        name = self.name or ""
        size = self.size_to_text() or ""
        file_extension = (
            self.image_link.split(".")[-1]
            if self.image_link and "." in self.image_link
            else ""
        )
        return f"{god} {name} {size}.{file_extension}".replace(" +", "")

    def __str__(self) -> str:
        return f"{self.god}: {self.name} {self.size}"
