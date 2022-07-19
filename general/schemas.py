from datetime import datetime, timedelta
from pydantic import BaseModel
from general.enums import TimeframeEnum


class SearchTerm(BaseModel):
    """
    Basemodel to get a str in API
    """
    searchTerm: str


class AddressDict(BaseModel):
    """
    Based model for address dict
    """
    address: dict


class DeliveryForm(BaseModel):
    """
    Basic model of a user delivery form
    """
    user: str
    timeslotid: int
