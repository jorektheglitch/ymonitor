from enum import Enum


class Intervals(Enum):
    hour = 1
    day = 24
    week = 24 * 7
    halfmounth = 24 * 7 * 2
    all = 2 ** 24
