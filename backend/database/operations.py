from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from .models import FlightOffer, FlightAmenity, Hotel, HotelOffer, HotelSentiment,SearchHistory
import json
import hashlib
from .db_init import get_session
from datetime import datetime, timedelta


class FlightOperations:
    def __init__(self, session: Session):
        self.session = session

    def save_flight_offers(self, flight_data: Dict[str, Any], search_params: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            flights = flight_data.get('data', [])
            saved_count = 0
            all_flight_ids = []  # 存储所有航班ID

            for flight in flights:
                flight_id = flight.get('id')
                all_flight_ids.append(flight_id)  # 记录所有ID

                # 检查是否已存在
                existing = self.session.query(FlightOffer).filter(FlightOffer.id == flight_id).first()
                if existing:
                    continue

                # 创建航班记录
                flight_offer = self._create_flight_offer(flight, search_params)
                self.session.add(flight_offer)

                # 创建便利设施记录
                self._create_amenities(flight, flight_id)

                saved_count += 1


            self.session.commit()

            return {
                "success": True,
                "saved_count": saved_count,
                "total_flights": len(all_flight_ids),
                "flight_ids": all_flight_ids  # 返回所有航班ID
            }

        except Exception as e:
            self.session.rollback()
            return {"success": False, "error": str(e)}

    def _create_flight_offer(self, flight: Dict[str, Any], search_params: Dict[str, Any]) -> FlightOffer:
        """创建航班报价记录"""
        # 提取行程信息
        itinerary = flight['itineraries'][0] if flight.get('itineraries') else {}
        segment = itinerary.get('segments', [{}])[0] if itinerary.get('segments') else {}

        # 提取价格信息
        price = flight.get('price', {})

        # 提取乘客详情
        traveler_pricing = flight.get('travelerPricings', [{}])[0] if flight.get('travelerPricings') else {}
        fare_detail = traveler_pricing.get('fareDetailsBySegment', [{}])[0] if traveler_pricing.get(
            'fareDetailsBySegment') else {}

        return FlightOffer(
            id=flight.get('id'),
            source=flight.get('source'),
            instant_ticketing_required=flight.get('instantTicketingRequired', False),
            non_homogeneous=flight.get('nonHomogeneous', False),
            one_way=flight.get('oneWay', False),
            is_upsell_offer=flight.get('isUpsellOffer', False),
            last_ticketing_date=flight.get('lastTicketingDate'),
            last_ticketing_date_time=flight.get('lastTicketingDateTime'),
            number_of_bookable_seats=flight.get('numberOfBookableSeats', 0),
            departure_iata=segment.get('departure', {}).get('iataCode'),
            arrival_iata=segment.get('arrival', {}).get('iataCode'),
            departure_time=segment.get('departure', {}).get('at'),
            arrival_time=segment.get('arrival', {}).get('at'),
            carrier_code=segment.get('carrierCode'),
            flight_number=segment.get('number'),
            aircraft_code=segment.get('aircraft', {}).get('code'),
            operating_carrier=segment.get('operating', {}).get('carrierName') or segment.get('operating', {}).get(
                'carrierCode'),
            duration=itinerary.get('duration'),
            currency=price.get('currency'),
            total_price=float(price.get('total', 0)),
            base_price=float(price.get('base', 0)),
            grand_total=float(price.get('grandTotal', 0)),
            cabin_class=fare_detail.get('cabin'),
            fare_basis=fare_detail.get('fareBasis'),
            branded_fare=fare_detail.get('brandedFare'),
            included_checked_bags=str(fare_detail.get('includedCheckedBags', {})),
            included_cabin_bags=str(fare_detail.get('includedCabinBags', {})),
            search_origin=search_params.get('origin') if search_params else None,
            search_destination=search_params.get('destination') if search_params else None,
            search_date=search_params.get('departure_date') if search_params else None,
            travel_class=search_params.get('travel_class') if search_params else None,
            raw_data=json.dumps(flight, ensure_ascii=False)
        )

    def _create_amenities(self, flight: Dict[str, Any], flight_offer_id: str):
        """创建便利设施记录"""
        traveler_pricings = flight.get('travelerPricings', [])
        for traveler in traveler_pricings:
            fare_details = traveler.get('fareDetailsBySegment', [])
            for fare_detail in fare_details:
                amenities = fare_detail.get('amenities', [])
                for amenity in amenities:
                    amenity_record = FlightAmenity(
                        flight_offer_id=flight_offer_id,
                        description=amenity.get('description'),
                        is_chargeable=amenity.get('isChargeable', False),
                        amenity_type=amenity.get('amenityType'),
                        amenity_provider=amenity.get('amenityProvider', {}).get('name')
                    )
                    self.session.add(amenity_record)


class HotelOperations:
    def __init__(self, session: Session):
        self.session = session

    def save_hotels(self, hotel_data: Dict[str, Any], search_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """保存酒店数据"""
        try:
            hotels = hotel_data.get('data', [])
            saved_count = 0
            hotel_ids = []

            for hotel in hotels:
                hotel_id = hotel.get('hotelId')
                hotel_ids.append(hotel_id)

                # 检查是否已存在
                existing = self.session.query(Hotel).filter(Hotel.id == hotel_id).first()
                if existing:
                    print(f"🔄 酒店已存在，跳过保存: {hotel_id}")
                    continue

                # 创建酒店记录
                hotel_record = self._create_hotel(hotel, search_params)
                self.session.add(hotel_record)

                # 创建设施记录
                self._create_hotel_amenities(hotel, hotel_id)

                saved_count += 1
                print(f"✅ 保存新酒店: {hotel_id}")

            self.session.commit()

            return {
                "success": True,
                "saved_count": saved_count,
                "hotel_ids": hotel_ids,
                "total_hotels": len(hotel_ids)
            }

        except Exception as e:
            self.session.rollback()
            return {"success": False, "error": str(e)}

    def _create_hotel(self, hotel: Dict[str, Any], search_params: Dict[str, Any]) -> Hotel:
        """创建酒店记录"""
        geo_code = hotel.get('geoCode', {})
        address = hotel.get('address', {})
        distance = hotel.get('distance', {})

        return Hotel(
            id=hotel.get('hotelId'),
            chain_code=hotel.get('chainCode'),
            iata_code=hotel.get('iataCode'),
            dupe_id=hotel.get('dupeId'),
            name=hotel.get('name'),
            hotel_id=hotel.get('hotelId'),
            latitude=geo_code.get('latitude'),
            longitude=geo_code.get('longitude'),
            country_code=address.get('countryCode'),
            postal_code=address.get('postalCode'),
            city_name=address.get('cityName'),
            address_lines=json.dumps(address.get('lines', []), ensure_ascii=False),
            distance_value=distance.get('value'),
            distance_unit=distance.get('unit'),
            rating=hotel.get('rating'),
            search_latitude=search_params.get('latitude') if search_params else None,
            search_longitude=search_params.get('longitude') if search_params else None,
            search_radius=search_params.get('radius') if search_params else None,
            search_radius_unit=search_params.get('radiusUnit') if search_params else None,
            master_chain_code=hotel.get('masterChainCode'),
            last_update=hotel.get('lastUpdate'),
            raw_data=json.dumps(hotel, ensure_ascii=False)
        )

    def _create_hotel_amenities(self, hotel: Dict[str, Any], hotel_id: str):
        """创建酒店设施记录"""
        # 这里可以从其他API获取酒店设施信息
        # 暂时留空，后续可以扩展
        pass

    def get_hotel_by_id(self, hotel_id: str) -> Optional[Hotel]:
        """根据ID获取酒店"""
        return self.session.query(Hotel).filter(Hotel.id == hotel_id).first()

    def get_hotels_by_location(self, latitude: float, longitude: float, radius: int = 10) -> List[Hotel]:
        """根据位置获取酒店"""
        return self.session.query(Hotel).filter(
            Hotel.search_latitude == latitude,
            Hotel.search_longitude == longitude,
            Hotel.search_radius == radius
        ).all()

    def get_hotel_stats(self) -> Dict[str, Any]:
        """获取酒店统计信息"""
        from sqlalchemy import func

        total_hotels = self.session.query(Hotel).count()

        # 按评级统计
        rating_stats = self.session.query(
            Hotel.rating,
            func.count(Hotel.id)
        ).group_by(Hotel.rating).all()

        # 按城市统计
        city_stats = self.session.query(
            Hotel.city_name,
            func.count(Hotel.id)
        ).group_by(Hotel.city_name).all()

        return {
            "total_hotels": total_hotels,
            "rating_distribution": dict(rating_stats),
            "city_distribution": dict(city_stats)
        }

    def save_hotel_offers(self, hotel_offers_data: Dict[str, Any], search_params: Dict[str, Any] = None) -> Dict[
        str, Any]:
        """保存酒店报价信息"""
        try:
            offers_data = hotel_offers_data.get('data', [])
            saved_count = 0
            hotel_ids = []

            for hotel_offer in offers_data:
                hotel_id = hotel_offer.get('hotel', {}).get('hotelId')
                if hotel_id:
                    hotel_ids.append(hotel_id)

                # 处理每个酒店的报价
                offers = hotel_offer.get('offers', [])
                for offer in offers:
                    offer_id = offer.get('id')

                    # 检查报价是否已存在
                    existing_offer = self.session.query(HotelOffer).filter(HotelOffer.id == offer_id).first()
                    if existing_offer:
                        continue

                    # 创建酒店报价记录
                    offer_record = self._create_hotel_offer(offer, hotel_offer, search_params)
                    self.session.add(offer_record)
                    saved_count += 1

            self.session.commit()

            return {
                "success": True,
                "saved_count": saved_count,
                "hotel_ids": list(set(hotel_ids)),  # 去重
                "total_offers": saved_count
            }

        except Exception as e:
            self.session.rollback()
            return {"success": False, "error": str(e)}

    def save_hotel_sentiments(self, sentiments_data: Dict[str, Any]) -> Dict[str, Any]:
        """保存酒店评价信息"""
        try:
            sentiments = sentiments_data.get('data', [])
            saved_count = 0
            hotel_ids = []

            for sentiment in sentiments:
                hotel_id = sentiment.get('hotelId')
                if hotel_id:
                    hotel_ids.append(hotel_id)

                # 检查评价是否已存在
                existing_sentiment = self.session.query(HotelSentiment).filter(
                    HotelSentiment.hotel_id == hotel_id
                ).first()

                if existing_sentiment:
                    # 更新现有评价
                    self._update_hotel_sentiment(existing_sentiment, sentiment)
                    saved_count += 1
                    print(f"🔄 更新酒店评价: {hotel_id}")
                else:
                    # 创建新评价记录
                    sentiment_record = self._create_hotel_sentiment(sentiment)
                    self.session.add(sentiment_record)
                    saved_count += 1
                    print(f"✅ 保存酒店评价: {hotel_id}")

            self.session.commit()

            return {
                "success": True,
                "saved_count": saved_count,
                "hotel_ids": hotel_ids,
                "total_sentiments": saved_count
            }

        except Exception as e:
            self.session.rollback()
            return {"success": False, "error": str(e)}

    def _create_hotel_offer(self, offer: Dict[str, Any], hotel_offer: Dict[str, Any],
                            search_params: Dict[str, Any]) -> HotelOffer:
        """创建酒店报价记录"""
        hotel_info = hotel_offer.get('hotel', {})
        price_info = offer.get('price', {})
        room_info = offer.get('room', {})
        guests_info = offer.get('guests', {})
        policies_info = offer.get('policies', {})

        return HotelOffer(
            id=offer.get('id'),
            hotel_id=hotel_info.get('hotelId'),
            check_in_date=offer.get('checkInDate'),
            check_out_date=offer.get('checkOutDate'),
            rate_code=offer.get('rateCode'),
            room_type=room_info.get('type'),
            room_description=room_info.get('description', {}).get('text'),
            adults=guests_info.get('adults', 0),
            children=guests_info.get('children', 0),
            currency=price_info.get('currency'),
            base_price=float(price_info.get('base', 0)),
            total_price=float(price_info.get('total', 0)),
            payment_type=policies_info.get('paymentType'),
            refundable=policies_info.get('refundable', {}).get('cancellationRefund'),
            raw_data=json.dumps(offer, ensure_ascii=False)
        )

    def _create_hotel_sentiment(self, sentiment: Dict[str, Any]) -> HotelSentiment:
        """创建酒店评价记录"""
        sentiments = sentiment.get('sentiments', {})

        return HotelSentiment(
            hotel_id=sentiment.get('hotelId'),
            overall_rating=sentiment.get('overallRating'),
            number_of_reviews=sentiment.get('numberOfReviews'),
            number_of_ratings=sentiment.get('numberOfRatings'),
            staff_rating=sentiments.get('staff'),
            location_rating=sentiments.get('location'),
            service_rating=sentiments.get('service'),
            room_comforts_rating=sentiments.get('roomComforts'),
            internet_rating=sentiments.get('internet'),
            sleep_quality_rating=sentiments.get('sleepQuality'),
            value_for_money_rating=sentiments.get('valueForMoney'),
            facilities_rating=sentiments.get('facilities'),
            catering_rating=sentiments.get('catering'),
            points_of_interest_rating=sentiments.get('pointsOfInterest'),
            raw_data=json.dumps(sentiment, ensure_ascii=False)
        )

    def _update_hotel_sentiment(self, existing: HotelSentiment, sentiment: Dict[str, Any]):
        """更新酒店评价记录"""
        sentiments = sentiment.get('sentiments', {})

        existing.overall_rating = sentiment.get('overallRating', existing.overall_rating)
        existing.number_of_reviews = sentiment.get('numberOfReviews', existing.number_of_reviews)
        existing.number_of_ratings = sentiment.get('numberOfRatings', existing.number_of_ratings)
        existing.staff_rating = sentiments.get('staff', existing.staff_rating)
        existing.location_rating = sentiments.get('location', existing.location_rating)
        existing.service_rating = sentiments.get('service', existing.service_rating)
        existing.room_comforts_rating = sentiments.get('roomComforts', existing.room_comforts_rating)
        existing.internet_rating = sentiments.get('internet', existing.internet_rating)
        existing.sleep_quality_rating = sentiments.get('sleepQuality', existing.sleep_quality_rating)
        existing.value_for_money_rating = sentiments.get('valueForMoney', existing.value_for_money_rating)
        existing.facilities_rating = sentiments.get('facilities', existing.facilities_rating)
        existing.catering_rating = sentiments.get('catering', existing.catering_rating)
        existing.points_of_interest_rating = sentiments.get('pointsOfInterest', existing.points_of_interest_rating)
        existing.raw_data = json.dumps(sentiment, ensure_ascii=False)


class SearchOperations:
    """搜索相关数据库操作"""

    def __init__(self, session: Session):
        self.session = session

    def save_search_result(self, search_data: Dict[str, Any]) -> bool:
        """保存搜索结果到数据库"""
        try:
            search_record = SearchHistory(
                query=search_data.get("query", ""),
                intent_type=search_data.get("intent_type", "通用"),
                location=search_data.get("location", ""),
                search_results=search_data.get("search_results", {}),
                result_count=search_data.get("result_count", 0),
                raw_data=json.dumps(search_data.get("search_results", {}), ensure_ascii=False),
                search_timestamp=datetime.fromisoformat(search_data.get("search_timestamp")) if search_data.get(
                    "search_timestamp") else datetime.utcnow()
            )

            self.session.add(search_record)
            self.session.commit()
            print(f"✅ 搜索记录已保存: {search_data.get('query')}")
            return True

        except Exception as e:
            print(f"❌ 保存搜索记录失败: {e}")
            self.session.rollback()
            return False

    def get_search_history(self, limit: int = 10) -> List[Dict]:
        """获取搜索历史记录"""
        try:
            history = self.session.query(SearchHistory).order_by(SearchHistory.created_at.desc()).limit(limit).all()
            return [item.to_dict() for item in history]
        except Exception as e:
            print(f"❌ 获取搜索历史失败: {e}")
            return []


    def get_search_statistics(self) -> Dict[str, Any]:
        """获取搜索统计信息"""
        try:
            total_searches = self.session.query(SearchHistory).count()

            intent_stats = {}
            intents = self.session.query(SearchHistory.intent_type).distinct().all()
            for intent in intents:
                intent_type = intent[0]
                count = self.session.query(SearchHistory).filter_by(intent_type=intent_type).count()
                intent_stats[intent_type] = count

            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_searches = self.session.query(SearchHistory).filter(SearchHistory.created_at >= yesterday).count()

            return {
                "total_searches": total_searches,
                "recent_searches_24h": recent_searches,
                "intent_breakdown": intent_stats
            }
        except Exception as e:
            print(f"❌ 获取搜索统计失败: {e}")
            return {}


# 便捷函数
def save_search_result(search_data: Dict[str, Any]) -> bool:
    """保存搜索结果的便捷函数"""
    session = get_session()
    try:
        ops = SearchOperations(session)
        return ops.save_search_result(search_data)
    finally:
        session.close()


def get_search_history(limit: int = 10) -> List[Dict]:
    """获取搜索历史的便捷函数"""
    session = get_session()
    try:
        ops = SearchOperations(session)
        return ops.get_search_history(limit)
    finally:
        session.close()


def save_to_cache(query: str, intent_type: str, location: str, search_data: Dict[str, Any]) -> bool:
    """保存到缓存的便捷函数"""
    session = get_session()
    try:
        ops = SearchOperations(session)
        return ops.save_to_cache(query, intent_type, location, search_data)
    finally:
        session.close()


def get_from_cache(query: str, intent_type: str, location: str) -> Optional[Dict[str, Any]]:
    """从缓存获取的便捷函数"""
    session = get_session()
    try:
        ops = SearchOperations(session)
        return ops.get_from_cache(query, intent_type, location)
    finally:
        session.close()


def get_search_statistics() -> Dict[str, Any]:
    """获取搜索统计的便捷函数"""
    session = get_session()
    try:
        ops = SearchOperations(session)
        return ops.get_search_statistics()
    finally:
        session.close()