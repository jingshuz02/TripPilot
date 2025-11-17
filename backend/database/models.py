from sqlalchemy import create_engine, Column, String, Integer, Float, JSON, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime


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




class HotelOffer(Base):
    __tablename__ = 'hotel_offers'

    id = Column(String(50), primary_key=True)
    hotel_id = Column(String(50), ForeignKey('hotels.id'))
    # 入住信息
    check_in_date = Column(String(20))
    check_out_date = Column(String(20))
    rate_code = Column(String(50))

    # 房间信息
    room_type = Column(String(50))
    room_description = Column(Text)

    # 客人信息
    adults = Column(Integer)
    children = Column(Integer)

    # 价格信息
    currency = Column(String(10))
    base_price = Column(Float)
    total_price = Column(Float)

    # 政策信息
    payment_type = Column(String(50))
    refundable = Column(String(50))

    # 原始数据
    raw_data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    hotel = relationship("Hotel")


class HotelSentiment(Base):
    __tablename__ = 'hotel_sentiments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    hotel_id = Column(String(50), ForeignKey('hotels.id'))

    # 评价信息
    overall_rating = Column(Integer)
    number_of_reviews = Column(Integer)
    number_of_ratings = Column(Integer)

    # 细分评价
    staff_rating = Column(Integer)
    location_rating = Column(Integer)
    service_rating = Column(Integer)
    room_comforts_rating = Column(Integer)
    internet_rating = Column(Integer)
    sleep_quality_rating = Column(Integer)
    value_for_money_rating = Column(Integer)
    facilities_rating = Column(Integer)
    catering_rating = Column(Integer)
    points_of_interest_rating = Column(Integer)

    # 原始数据
    raw_data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    hotel = relationship("Hotel")


class SearchHistory(Base):
    __tablename__ = 'search_history'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 搜索信息
    query = Column(String(500), nullable=False)
    intent_type = Column(String(50), nullable=False)
    location = Column(String(100))

    # 搜索结果
    search_results = Column(JSON)
    result_count = Column(Integer, default=0)

    # 原始数据和时间戳
    raw_data = Column(Text)
    search_timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'query': self.query,
            'intent_type': self.intent_type,
            'location': self.location,
            'result_count': self.result_count,
            'search_timestamp': self.search_timestamp.isoformat() if self.search_timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class CachedSearchData(Base):
    __tablename__ = 'cached_search_data'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 缓存键
    query_hash = Column(String(64), unique=True, nullable=False)
    intent_type = Column(String(50), nullable=False)
    location = Column(String(100), nullable=False)

    # 缓存数据
    search_data = Column(JSON, nullable=False)

    # 时间信息
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def is_expired(self):
        return datetime.utcnow() > self.expires_at



