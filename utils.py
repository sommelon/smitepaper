import argparse
from functools import lru_cache
import logging
import warnings
from constants import ALL_SIZES, GODS_FILENAME
import requests
from requests.exceptions import InvalidURL, MissingSchema


f = open(GODS_FILENAME, "r")
gods = f.read().splitlines()
f.close()


def valid_input(message, choices=("",)):
    answer = input(message)
    while answer not in choices:
        answer = input(message)
    return answer


@lru_cache()  # Use a separate cache so we don't ask for the same skin name multiple times.
def _ask_for_god_name(skin_name):
    # TODO: Add file caching
    god = input(
        f"Couldn't find god name for skin {skin_name}. Enter the god name or skip by pressing enter: "
    )
    logging.info(f"Couldn't guess god from skin {skin_name}. User entered: {god}.")
    return god if god else None


@lru_cache()
def get_god_name(skin_name):
    name_map = {
        "AMC": "Ah Muzen Cab",
        "AhMuzen Cab": "Ah Muzen Cab",
        "Isis": "Eset",
        "Chang’e": "Chang'e",
        "Sun Wukon": "Sun Wukong",
        "Earl Wubert": "Sun Wukong Earl Wubert",
        "Neith’s Biggest Fan Zhong Kui": "Zhong Kui",
    }

    for k, v in name_map.items():
        skin_name = skin_name.replace(k, v)

    for god in gods:
        if god.lower() in skin_name.lower():
            logging.info(f"Guessed god {god} from skin {skin_name}")
            return god
    return _ask_for_god_name(skin_name)


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
