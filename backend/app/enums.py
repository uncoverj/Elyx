from enum import Enum


class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class MediaType(str, Enum):
    photo = "photo"
    video = "video"


class StatsSource(str, Enum):
    manual = "manual"
    riot = "riot"
    steam = "steam"
    other = "other"
