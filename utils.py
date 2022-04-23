import argparse
from functools import lru_cache
import requests
import sys
from requests.exceptions import InvalidURL, MissingSchema


GODS_FILENAME = "gods.txt"

f = open(GODS_FILENAME, "r")
gods = f.read().splitlines()
f.close()


@lru_cache()  # Use a separate cache so we don't ask for the same skin name multiple times.
def _ask_for_god_name(skin_name):
    # TODO: Add file caching
    god = input(
        f"Couldn't find god name for skin {skin_name}. Enter the god name or skip by pressing enter: "
    )
    return god if god else None


@lru_cache()
def get_god_name(skin_name):

    if skin_name == "Neith’s Biggest Fan Zhong Kui":
        return "Zhong Kui"

    name_map = {
        "AMC": "Ah Muzen Cab",
        "AhMuzen Cab": "Ah Muzen Cab",
        "Isis": "Eset",
        "Chang’e": "Chang'e",
        "Sun Wukon": "Sun Wukong",
        "Earl Wubert": "Sun Wukong Earl Wubert",
    }
    for k, v in name_map.items():
        skin_name = skin_name.replace(k, v)

    for god in gods:
        if god.lower() in skin_name.lower():
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
        return width, height
    except Exception:
        raise argparse.ArgumentTypeError("Coordinates must be x,y,z")


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

    def to_csv(self):
        size = self.size_to_text()
        return [self.name, self.image_link, size]

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
