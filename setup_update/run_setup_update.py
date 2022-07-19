import json
import time
from typing import Set
import logging
import holidayapi
import constants as const
from datetime import datetime, date
from database.db_setup import SessionLocal
from repos import timeslot_repo, address_repo
import schedule


# TODO: Check if thies week it's the last of week of the year and take also the next years holidays.
# TODO: Optimize it by taking only the holidays in that are in the following week.

def get_holidays_by_dates() -> Set[date]:
    """
    Get all the holidays dates from holiday api as Datetime,
    Will try 5 times to connect to the API and wait 3 second between attempts.
    :return: Dictionary of all the holiday dates as Datetime objects.
    """
    tries = 5
    while tries:
        try:
            hapi = holidayapi.v1(const.HOLIDAY_API_KEY)  # Get holidays from API
            # Take only the dates and convert them to Datetime
            return {datetime.strptime(holiday["date"], '%Y-%m-%d').date() for holiday in
                    hapi.holidays({'country': 'IL', 'year': '2021', })["holidays"]}
        except Exception as e:
            # If no more tries will raise a connection error
            if not tries:
                logging.exception("Holiday API problem")
                raise e
            # Deduct tries and sleep for 3 seconds
            tries -= 1
            time.sleep(3)


def formatted_datetime(date_str: str) -> datetime:
    """
    Format a str to a Datetime
    :param date_str: string of a date
    :return: Datetime object of the date string
    """
    try:
        return datetime.strptime(date_str, '%d-%m-%Y,%H:%M')
    except AttributeError as e:
        logging.exception(f"Issue formatting date of timeslot: {date_str}")
        raise e


def setup() -> None:
    """
    This function runs every everytime and set up the next week deliveries
    Will get the deliveries from "courier_API.json" and add them if they are not on holiday
    or the timeslot is already in the database.
    """
    try:
        with open(
                "setup_update/courier_API.json") as file, SessionLocal() as db:  # Get the deliveries and open a session with the DB
            data = json.load(file)  # Load the file as json
            holidays = get_holidays_by_dates()  # Get all the holidays
            for timeslot_json in data["timeslots"]:  # Check each timeslot
                # Get the start and end as Datetime objects.
                start, end = formatted_datetime(timeslot_json["start"]), formatted_datetime(timeslot_json["end"])

                # Check if start or end are not holidays + check if the timeslot is not in the DB
                if start.date() not in holidays and end.date() not in holidays \
                        and not timeslot_repo.get_timeslot_by_start_end(start=start, end=end, db=db):

                    # Create the new timeslot and address (if needed) and add to the DB
                    new_timeslot = timeslot_repo.create_timeslot(start, end, db)
                    address_repo.insert_timeslot_to_addresses(timeslot=new_timeslot,
                                                              addresses=timeslot_json["addresses"], db=db)
            # Commit the data after everything was added properly
            db.commit()
    except OSError as os:
        logging.exception("Could not open file")
        print(os)
    except json.decoder.JSONDecodeError as js:
        logging.exception("Could not load file to Json")
        print(js)
    except Exception as ex:
        logging.exception("Issue when setting up")
        print(ex)


def run():
    """
    A Scheduler to update the TimeSlots every week.
    """
    setup()
    schedule.every(1).week.do(setup)
