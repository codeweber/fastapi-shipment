from enum import Enum


class ShipmentTag(str, Enum):
    EXPRESS = "express"
    STANDARD = "standard"
    FRAGILE = "fragile"
    HEAVY = "heavy"
    INTERNATIONAL = "international"
    DOMESTIC = "domestic"
    RETURN = "return"
    