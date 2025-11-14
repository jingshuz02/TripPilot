from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from .models import FlightOffer, FlightAmenity, Hotel, HotelAmenity
import json


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
            amenities=json.dumps([], ensure_ascii=False),  # 可以从其他API获取
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