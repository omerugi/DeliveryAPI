import logging
from typing import List

from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from database.models.models import Delivery, TimeSlot, TimeslotsAddress
from general.enums import StatusEnum
from datetime import datetime, date
from sqlalchemy import func


def get_delivery_by_id(delivery_id: int, db: Session) -> Delivery:
    """
    Getting a delivery based on the id.
    :param delivery_id: The id of the delivery.
    :param db: DB Session.
    """
    try:
        return db.query(Delivery).filter(Delivery.id == delivery_id).first()
    except Exception as sq:
        db.rollback()
        logging.exception(f"Issue getting delivery by id - {delivery_id}")
        raise sq


def get_deliveries_by_timeframe_date(start_timeframe: date, end_timeframe: date, db: Session):
    """
    Getting all the deliveries with in a timeframe - stat until end.
    :param start_timeframe: The beginning of the timeframe.
    :param end_timeframe: The end of the timeframe.
    :param db: DB Session.
    """
    try:
        return db.query(Delivery).join(TimeSlot) \
            .filter(and_(start_timeframe <= func.date(TimeSlot.start),
                         func.date(TimeSlot.start) <= end_timeframe)) \
            .all()
    except Exception as sq:
        db.rollback()
        logging.exception(f"Issue getting delivery by timeframe - {start_timeframe, end_timeframe}")
        raise sq


def deliveries_to_set(deliveries: List) -> set:
    """
    Changing a list of deliveries into a set.
    :param deliveries: List of the deliveries.
    """
    try:
        return {delivery._asdict() for delivery in deliveries}
    except Exception as e:
        logging.exception("Issue when making deliveries as sets")
        raise e


def count_deliveries_by_timeslot_id(timeslotid: int, db: Session) -> int:
    """
    Counts the number of active deliveries based on a timeslot id
    """
    try:
        return db.query(Delivery).filter(
            and_(Delivery.status == StatusEnum.active, Delivery.timeslot.id == timeslotid)).count()
    except Exception as sq:
        db.rollback()
        logging.exception(f"Issue when counting deliveries by timeslot id {timeslotid}")
        raise sq


def is_valid_timeslot(timeslotid: int, db: Session) -> bool:
    """
    Check if there is more than two deliveries on the same timeslot.
    :param timeslotid:
    :param db:
    :return:
    """
    try:
        return count_deliveries_by_timeslot_id(timeslotid, db) > 2
    except Exception as e:
        raise e


def create_new_delivery(user: str, timeslot: TimeSlot, db: Session):
    """
    Creates a new delivery.
    :param user: The user who asked for the delivery.
    :param timeslot: The timeslot the user booked for the delivery.
    :param db: DB Session.
    :return: A new delivery.
    """
    try:
        new_del = Delivery(status=StatusEnum.active, user=user, timeslot=timeslot)
        db.add(new_del)
        return new_del
    except Exception as sq:
        db.rollback()
        logging.exception("Issue creating a new delivery")
        raise sq


def update_delivery_status(status: StatusEnum, delivery_id: int, db: Session) -> None:
    """
    Updates the delivery status.
    :param status: The new status.
    :param delivery_id: The id of the delivery that is updating.
    :param db: DB Session
    """
    try:
        db.query(Delivery).filter(Delivery.id == delivery_id).update({"status": status})
    except Exception as sq:
        db.rollback()
        logging.exception("Issue when tried to update delivery status")
        raise sq


def update_by_id_and_check_status(status: StatusEnum, delivery_id: int, db: Session) -> bool:
    """
    Will do an update and validate.
    :param status: The new status.
    :param delivery_id: The id of the delivery that is updating.
    :param db: DB Session.
    :return: a Bool telling if the update worked.
    """
    try:
        update_delivery_status(status, delivery_id, db)
        return get_delivery_by_id(delivery_id, db).status == status
    except Exception as e:
        raise e
