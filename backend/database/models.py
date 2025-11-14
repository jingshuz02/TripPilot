from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import json

Base = declarative_base()


class FlightOffer(Base):
    __tablename__ = 'flight_offers'

    id = Column(String(50), primary_key=True)
    source = Column(String(50))
    instant_ticketing_required = Column(Boolean)
    non_homogeneous = Column(Boolean)
    one_way = Column(Boolean)
    is_upsell_offer = Column(Boolean)
    last_ticketing_date = Column(String(20))
    last_ticketing_date_time = Column(String(20))
    number_of_bookable_seats = Column(Integer)

    # 航班信息
    departure_iata = Column(String(10))
    arrival_iata = Column(String(10))
    departure_time = Column(String(25))
    arrival_time = Column(String(25))
    carrier_code = Column(String(10))
    flight_number = Column(String(10))
    aircraft_code = Column(String(10))
    operating_carrier = Column(String(100))
    duration = Column(String(20))

    # 价格信息
    currency = Column(String(10))
    total_price = Column(Float)
    base_price = Column(Float)
    grand_total = Column(Float)

    # 其他信息
    cabin_class = Column(String(50))
    fare_basis = Column(String(50))
    branded_fare = Column(String(100))
    included_checked_bags = Column(String(100))
    included_cabin_bags = Column(String(100))

    # 搜索参数
    search_origin = Column(String(10))
    search_destination = Column(String(10))
    search_date = Column(String(20))
    travel_class = Column(String(20))

    # 原始数据（用于调试）
    raw_data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    amenities = relationship("FlightAmenity", back_populates="flight_offer", cascade="all, delete-orphan")


class FlightAmenity(Base):
    __tablename__ = 'flight_amenities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    flight_offer_id = Column(String(50), ForeignKey('flight_offers.id'))
    description = Column(String(200))
    is_chargeable = Column(Boolean)
    amenity_type = Column(String(50))
    amenity_provider = Column(String(100))

    # 关系
    flight_offer = relationship("FlightOffer", back_populates="amenities")


class Hotel(Base):
    __tablename__ = 'hotels'

    id = Column(String(50), primary_key=True)
    chain_code = Column(String(10))
    iata_code = Column(String(10))
    dupe_id = Column(Integer)
    name = Column(String(200))
    hotel_id = Column(String(50))

    # 地理信息
    latitude = Column(Float)
    longitude = Column(Float)

    # 地址信息
    country_code = Column(String(10))
    postal_code = Column(String(20))
    city_name = Column(String(100))
    address_lines = Column(Text)  # 存储为JSON字符串

    # 距离信息
    distance_value = Column(Float)
    distance_unit = Column(String(10))

    # 评级和设施
    rating = Column(Integer)
    amenities = Column(Text)  # 存储为JSON字符串

    # 搜索参数
    search_latitude = Column(Float)
    search_longitude = Column(Float)
    search_radius = Column(Integer)
    search_radius_unit = Column(String(10))

    # 其他信息
    master_chain_code = Column(String(10))
    last_update = Column(String(25))

    # 原始数据
    raw_data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class HotelAmenity(Base):
    __tablename__ = 'hotel_amenities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    hotel_id = Column(String(50), ForeignKey('hotels.id'))
    amenity_name = Column(String(100))
    amenity_category = Column(String(50))

    # 关系
    hotel = relationship("Hotel")