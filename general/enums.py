import enum


class StatusEnum(enum.Enum):
    active = 1
    finished = 2
    canceled = 3


class TimeframeEnum(enum.Enum):
    daily = "daily"
    weekly = "weekly"
