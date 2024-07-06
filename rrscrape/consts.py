import re
from typing import Union

VALUE_TYPES = Union[str, int, float, None]
SCORE_PATTERN = re.compile(r"^\d+\.\d+ / \d+$")
COUNT_PATTERN = re.compile(r"^\d+(,\d+)*$")

GENERAL_COLUMNS = [
    "Number of Published Book(s)",  # source: amazon
    "Story Setting",  # source: rr + amazon (? unclear what this requirement is) + LLM
    "MC Gender",  # source: rr + amazon LLM
    "Steamy (18+/NSFW)",  # source: rr + amazon LLM
    "Subgenre",  # source: rr + amazon LLM
    "MC Sexual Orientation",  # source: rr + amazon LLM
]
RR_COLUMNS = [
    "RR Title",
    "RR Author",
    "RR Blurb",
    "RR First Chapter TS",
    "RR Overall Score",
    "RR Style Score" "RR Story Score" "RR Grammar Score" "RR Character Score" "RR Average Views",
    "RR Total Views",
    "RR Followers",
    "RR Ratings",
    "RR Tags",
    "RR Warnings",
    "RR Favorites",
    "RR Thumbnail URL",
    "RR Retrieved TS",
]
AMAZON_COLUMNS = [
    "Amazon Title",
    "Amazon Author",
    "Amazon Blurb",
    "Amazon Publisher",
    "Amazon Publication TS",
    "Amazon Series Length",
    "Amazon Rating",
    "Amazon Ratings Count",
    "Amazon Page Count",
]
AUDIBLE_COLUMNS = [
    "Audible Title",
    "Audible Publication TS",
    "Audible Rating",
    "Audible Ratings Count",
    "Audible Length",
]

COLS_ORDER = [
    "RR Title",
    "RR Author",
    "RR Overall Score",
    "RR Ratings",
    "RR Retrieved at",
    "RR Followers",
    "RR Pages",
    "Number of Published Book(s)",
    "Story Setting",
    "MC Gender",
    "Steamy (18+/NSFW)",
    "MC Sexual Orientation",
    "Subgenre",
    "RR Total Views",
    "RR Average Views",
    "RR Favorites",
    "RR Blurb",
    "RR Tags",
    "RR Warnings",
    "RR Thumbnail URL",
    "RR URL",
]
