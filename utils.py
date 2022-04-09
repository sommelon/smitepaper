from functools import lru_cache


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


class Wallpaper:
    def __init__(self, name, image_link, size):
        self.name = name
        self.image_link = image_link
        self.size = size

    def to_csv(self):
        size = f"{self.size[0]}x{self.size[1]}" if self.size else None
        return [self.name, self.image_link, size]
