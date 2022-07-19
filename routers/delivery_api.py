import logging

from fastapi import APIRouter, Response, Depends, status
from sqlalchemy.orm import Session
from database.db_setup import get_db
from general.schemas import SearchTerm, AddressDict, DeliveryForm
from repos import address_repo, timeslot_repo, deliveries_repo
from general.enums import StatusEnum
from general.enums import TimeframeEnum
from general import functions as func

router = APIRouter(
    tags=["delivery_api"]
)


@router.get("/")
async def root():
    return {"message": "Hello World!"}


@router.post("/resolve-address")
def resolve_address(searchTerm: SearchTerm):
    """
    Recives a string of an address and convert it to a formatted address from API.
    """
    try:
        for key, value in address_repo.format_address(searchTerm.searchTerm).items():
            print(f"{key}: {value}")
        return Response(status_code=status.HTTP_200_OK)
    except Exception as e:
        print(e)
    return Response(status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/timeslots")
def get_timeslots(address: AddressDict, db: Session = Depends(get_db)):
    """
    Change it from post to get.
    Returns all the timeslots based on an address as a set.
    Will return the set of the timeslots if valid address, otherwise will return an empty set.
    :param address: A formatted address.
    :param db: DB Session.
    :return: timeslots.
    """
    try:
        address = address_repo.get_address(address.address, db)
        # Check if the address was valid - if so, get all the timeslots
        timeslots = timeslot_repo.get_timeslots_by_address(address.id, db)
        ans = timeslot_repo.get_timeslots_to_set(timeslots) if address else {}

        # If ans is empty but there are timeslots in the DB - rais exception
        if not ans and timeslots:
            logging.exception("Set of timeslots is empty")
            raise Exception("Set of timeslots is empty")
        return ans
    except Exception as e:
        print(e)
        return Response(status_code=status.HTTP_400_BAD_REQUEST)


@router.put("/deliveries")
def book_delivery(delivery: DeliveryForm, db: Session = Depends(get_db)):
    """
    Book a new delivery, (change it from POST to PUT)
    :param delivery: A simple DeliveryForm with username and timeslot id.
    :param db: DB Session.
    """
    try:
        # Get the timeslot by id
        timeslot = timeslot_repo.get_timeslot_by_id(delivery.timeslotid, db)
        # Check if the timeslot exist and also has less than 2 deliveries.
        if timeslot and deliveries_repo.is_valid_timeslot(delivery.timeslotid, db):
            deliveries_repo.create_new_delivery(DeliveryForm.user, timeslot, db)
            db.commit()
            return Response(status_code=status.HTTP_201_CREATED)
    except Exception as e:
        print(e)
    return Response(status_code=status.HTTP_400_BAD_REQUEST)


# TODO: make the post and delete rout to the same update function.
@router.post("/deliveries/{DELIVERY_ID}/complete")
def complete_delivery(DELIVERY_ID: int, db: Session = Depends(get_db)):
    """
    Mark a delivery as complete.
    :param db: DB Session.
    :param DELIVERY_ID: The ID of the delivery we want to update.
    """
    try:
        if deliveries_repo.update_by_id_and_check_status(StatusEnum.finished, DELIVERY_ID, db):
            return Response(status_code=status.HTTP_200_OK)
    except Exception as e:
        print(e)
    return Response(status_code=status.HTTP_400_BAD_REQUEST)


@router.delete("/deliveries/{DELIVERY_ID}")
def delete_delivery(DELIVERY_ID: int, db: Session = Depends(get_db)):
    """
    Mark a delivery as cancelled.
    :param DELIVERY_ID: The ID of the delivery we want to update.
    :param db:DB Session.
    """
    try:
        if deliveries_repo.update_by_id_and_check_status(StatusEnum.canceled, DELIVERY_ID, db):
            return Response(status_code=status.HTTP_200_OK)
    except Exception as e:
        print(e)
    return Response(status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/deliveries/{TIME_FRAME}")
def get_todays_deliveries(TIME_FRAME: str, db: Session = Depends(get_db)):
    """
    Get all deliveries based on timeslots
    :param TIME_FRAME: Would tell us it it's weekly of daily
    :param db: DB Session.
    """
    try:
        start, end = func.get_timeframe(TimeframeEnum(TIME_FRAME))
        # Get all deliveries based on timeframe
        deliveries = deliveries_repo.get_deliveries_by_timeframe_date(start, end, db)

        # Format them to a set
        ans = deliveries_repo.deliveries_to_set(deliveries)
        if not ans and deliveries:
            logging.exception("Set of timeslots is empty")
            raise Exception("Set of timeslots is empty")
        return ans
    except Exception as e:
        print(e)
    return Response(status_code=status.HTTP_400_BAD_REQUEST)
