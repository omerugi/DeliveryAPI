import logging
from datetime import datetime, timedelta
from typing import Tuple

from general.enums import TimeframeEnum


def get_timeframe(frame: TimeframeEnum)-> Tuple:
    """
    Will return a tuple of time frame - start, end - based on the frame (Weekly / Daily)
    :return:
    """
    if frame == TimeframeEnum.daily:
        return datetime.now().date(), datetime.now().date()
    elif frame == TimeframeEnum.weekly:
        return datetime.now().date(), (datetime.now() + timedelta(days=7)).date()
    else:
        logging.exception(f"Issue with timeframe enum - {frame}")
        raise Exception("Issue with timeframe enum")
