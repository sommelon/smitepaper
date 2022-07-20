from functools import lru_cache
import logging
from constants import GODS_FILENAME
import requests
from collections import namedtuple
from requests.exceptions import InvalidURL, MissingSchema
import re


ALL_GODS = []
with open(GODS_FILENAME, "r") as f:
    ALL_GODS = f.read().splitlines()


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

    for god in ALL_GODS:
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


Size = namedtuple("Size", "width height")


class Wallpaper:
    SIZE_DELIMITER = "x"

    def __init__(self, name, image_link, size, god=None, slug=None):
        self.name = name
        self.image_link = image_link
        if isinstance(size, str):
            size = self.text_to_size(size)
        self.size = size
        self.god = god
        self.slug = slug

    def text_to_size(self, text):
        if isinstance(text, str):
            if Wallpaper.SIZE_DELIMITER not in text:
                raise ValueError(
                    f"Size {text} doesn't contain {Wallpaper.SIZE_DELIMITER}",
                )
            text = text.split(Wallpaper.SIZE_DELIMITER)
            return Size(*map(int, text))

        return Size(*text)

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

    def get_file_extension(self):
        return (
            self.image_link.split(".")[-1]
            if self.image_link and "." in self.image_link
            else "png"
        )

    def get_filepath(self, format_str):
        god = self.god or ""
        name = self.name or ""
        size = self.size_to_text() or ""
        file_extension = self.get_file_extension()
        return format_str.format(
            god=god, skin=name, size=size, extension=file_extension
        )

    def __str__(self) -> str:
        return f"{self.god}: {self.name} {self.size}"
