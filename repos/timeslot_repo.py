import logging
from typing import List

from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from database.models.models import TimeSlot, TimeslotsAddress
from datetime import datetime


def get_timeslot_by_start_end(start: datetime, end: datetime, db: Session) -> TimeSlot:
    """
    Get a timeslot based on the start and end datetime.
    """
    try:
        return db.query(TimeSlot).filter(and_(TimeSlot.start == start,
                                              TimeSlot.end == end)).first()
    except Exception as sq:
        db.rollback()
        logging.exception("Issue when getting a timeslot by start and end")
        raise sq


def get_timeslots_by_address(address: int, db: Session):
    """
    Get timeslot based on address.
    :param address: address id from db.
    :param db: db Session.
    """
    try:
        return db.query(TimeSlot).filter(TimeSlot.addressees.address_id == address).all()
    except Exception as sq:
        db.rollback()
        logging.exception("Issue when getting timeslots by address")
        raise sq


def get_timeslot_by_id(timeslotid: int, db: Session):
    try:
        return db.query(TimeSlot).filter(TimeSlot.id == timeslotid).first()
    except Exception as sq:
        db.rollback()
        logging.exception("Issue getting timeslot by id")
        raise sq


def get_timeslots_to_set(timeslots: List) -> set:
    """
    Change timeslots to set.
    :param timeslots : A list of timeslots.
    :return : A set of all the timeslots as set.
    """
    try:
        return {timeslot._asdict() for timeslot in timeslots}
    except Exception as e:
        logging.exception("Issue when formatting timeslots to set")
        raise e


def count_all_timeslots(db: Session)-> int:
    """
    Counts all the timeslots.
    :param db: DB Session.
    :return: int of the total number of timeslots.
    """
    try:
        return db.query(TimeSlot).all().count(TimeSlot.id)
    except Exception as sq:
        db.rollback()
        logging.exception("Issue getting all the timeslots")
        raise sq


def create_timeslot(start: datetime, end: datetime, db: Session) -> TimeSlot:
    """
    Creates and return a new timeslot.
    :param start: The start of the timeslot.
    :param end: The end of the timeslot.
    :param db: db Session.
    :return: The new TimeSlot.
    """
    try:
        timeslot = TimeSlot(start=start, end=end)
        db.add(timeslot)
        return timeslot
    except Exception as sq:
        db.rollback()
        logging.exception("Issue creating a new timeslot")
        raise sq
