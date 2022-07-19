import json
import logging
import time
from typing import List
from sqlalchemy import and_
from sqlalchemy.orm import Session
from database.models.models import Address, TimeslotsAddress, TimeSlot
import constants as const
import requests
from requests.structures import CaseInsensitiveDict


def create_address(address: dict, db: Session) -> Address:
    """
    Creates a new address in the DB
    :param address: A formatted address
    :param db: DB session
    :return: New address model
    """
    try:
        add = Address(street=address["street"],
                      address_line1=address["address_line1"],
                      address_line2=address["address_line2"],
                      country=address["country"],
                      postcode=address["postcode"],
                      city=address["city"],
                      country_code=address["country_code"],
                    )
        db.add(add)
        return add
    except Exception as sq:
        logging.exception("Issue when creating a new address")
        db.rollback()
        raise sq


def get_address(address: dict, db: Session) -> Address:
    """
    Get address from DB based on a formatted address
    :param address: Formatted address
    :param db: DB session
    :return: The address from the DB.
    """
    try:
        return db.query(Address).filter(and_(Address.street == address["street"],
                                             Address.address_line1 == address["address_line1"],
                                             Address.address_line2 == address["address_line2"],
                                             Address.country == address["country"],
                                             Address.postcode == address["postcode"],
                                             Address.city == address["city"],
                                             Address.country_code == address["country_code"]
                                             )
                                        ).first()
    except Exception as sq:
        db.rollback()
        logging.exception("Issue getting address by addresses dict")
        raise sq


def get_or_create_new(address: dict, db: Session) -> Address:
    """
    Will create new or get one from the DB is the address is already in.
    :param address: Formatted address
    :param db: DB session
    :return: The address from the DB / new one.
    """
    try:
        add = get_address(address, db)
        if not add:
            add = create_address(address, db)
        return add
    except Exception as e:
        raise e


def format_address(address: str):
    """
    Formatting an address from a string to Geoapi format.
    Will try to connect to Geoapi 5 times, between each attempt will wait 5 seconds.
    :return: Geoapi address format.
    """
    tries = 5
    while tries:
        try:
            address = address.replace(" ", "%20")
            url = f"https://api.geoapify.com/v1/geocode/search?text={address}&format=json&apiKey={const.GEO_API_KEY}"
            headers = CaseInsensitiveDict()
            headers["Accept"] = "application/json"
            content = requests.get(url, headers=headers).content
            json_api = json.loads(content)
            return json_api["results"][0]
        except json.decoder.JSONDecodeError as js:
            if not tries:
                logging.exception("Issue loading json of addresses")
                raise js
        except ConnectionError as co:
            if not tries:
                logging.exception("Error connecting to GEO API")
                raise co
        except Exception as e:
            logging.exception("Issue when formatting addresses")
            raise e
        tries -= 1
        time.sleep(5)


def insert_timeslot_to_addresses(timeslot: TimeSlot, addresses: List[str], db: Session) -> None:
    """
    Add the timeslot to the relevant addresses.
    :param timeslot: The timeslot that connects to the address.
    :param addresses: The addresses that are relevant to the timeslot.
    :param db: DB Session.
    """
    for address in addresses:
        try:
            add = get_or_create_new(format_address(address), db)
            timeslot.ad.append(add)
        except Exception as e:
            raise e
