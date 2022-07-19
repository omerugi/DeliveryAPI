from database.db_setup import Base
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from general.enums import StatusEnum


class Delivery(Base):
    """
    The delivery table format.
    """
    __tablename__ = 'deliveries'
    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(StatusEnum), nullable=False)
    timeslot = relationship("TimeSlot", back_populates="deliveries")
    timeslot_id = Column(Integer, ForeignKey("timeslots.id"))
    user = Column(String(50), nullable=False)


TimeslotsAddress = Table(
    "TimeslotsAddress",
    Base.metadata,
    Column("timeslot_id", ForeignKey("timeslots.id"), primary_key=True),
    Column("address_id", ForeignKey("addressees.id"), primary_key=True),
)


class TimeSlot(Base):
    """
    The timeslot table format.
    """
    __tablename__ = 'timeslots'
    id = Column(Integer, primary_key=True, index=True)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    deliveries = relationship("Delivery", back_populates="timeslot")
    ad = relationship("Address", secondary=TimeslotsAddress, back_populates="ts")


class Address(Base):
    """
    The Address table format.
    """
    __tablename__ = 'addressees'
    id = Column(Integer, primary_key=True, index=True)
    street = Column(String(50), nullable=False)
    address_line1 = Column(String(100), nullable=False)
    address_line2 = Column(String(100), nullable=False)
    country = Column(String(50), nullable=False)
    postcode = Column(String(50), nullable=False)
    city = Column(String(50), nullable=False)
    country_code = Column(String(4), nullable=False)
    ts = relationship("TimeSlot", secondary=TimeslotsAddress, back_populates="ad")
