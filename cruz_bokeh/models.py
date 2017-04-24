import mongoengine as me
import pandas as pd

__author__ = "Surya Bahubalendruni"


class Ride(me.Document):
	pickup_datetime = me.DateTimeField()
	dropoff_datetime = me.DateTimeField()
	pickup_zipcode = me.IntField()
	pickup_borough = me.StringField()
	pickup_county = me.StringField()
	pickup_long_lat = me.PointField()
	dropoff_zipcode = me.IntField()
	dropoff_borough = me.StringField()
	dropoff_county = me.StringField()
	dropoff_long_lat = me.PointField()
	total_amount = me.FloatField()
	fare_amount = me.FloatField()
	tip_amount = me.FloatField()
	passenger_count = me.IntField()
	trip_distance = me.FloatField()

	@me.queryset_manager
	def pickups_nearby(doc_cls, queryset, long, lat, distance):
		return queryset.filter(pickup_long_lat__near=[long, lat], pickup_long_lat__max_distance=distance).order_by('-pickup_datetime')

	@me.queryset_manager
	def dropoffs_nearby(doc_cls, queryset, long, lat, distance):
		return queryset.filter(dropoff_long_lat__near=[long, lat], dropoff_long_lat__max_distance=distance).order_by('-dropoff_datetime')

	def to_json(self):
		response = {"pickup_datetime": self.pickup_datetime,
					"dropoff_datetime": self.dropoff_datetime,
					"pickup_zipcode": self.pickup_zipcode,
					"pickup_borough": self.pickup_borough,
					"pickup_county": self.pickup_county,
					"pickup_long_lat": self.pickup_long_lat['coordinates'],
					"dropoff_zipcode": self.dropoff_zipcode,
					"dropoff_borough": self.dropoff_borough,
					"dropoff_county": self.dropoff_county,
					"dropoff_long_lat": self.dropoff_long_lat['coordinates'],
					"total_amount": self.total_amount,
					"fare_amount": self.fare_amount,
					"tip_amount": self.tip_amount,
					"passenger_count": self.passenger_count,
					"trip_distance": self.trip_distance
					}
		return response

	def to_series(self):
		response = pd.Series(
			{"pickup_datetime": self.pickup_datetime,
			 "dropoff_datetime": self.dropoff_datetime,
			 "pickup_zipcode": self.pickup_zipcode,
			 "pickup_borough": self.pickup_borough,
			 "pickup_county": self.pickup_county,
			 "pickup_long_lat": self.pickup_long_lat['coordinates'],
			 "dropoff_zipcode": self.dropoff_zipcode,
			 "dropoff_borough": self.dropoff_borough,
			 "dropoff_county": self.dropoff_county,
			 "dropoff_long_lat": self.dropoff_long_lat['coordinates'],
			 "total_amount": self.total_amount,
			 "fare_amount": self.fare_amount,
			 "tip_amount": self.tip_amount,
			 "passenger_count": self.passenger_count,
			 "trip_distance": self.trip_distance
			 })
		return response

	meta = {
		'indexes': [[("pickup_long_lat", "2dsphere"), ("pickup_datetime", 1)],
					[("dropoff_long_lat", "2dsphere"), ("dropoff_datetime", 1)],
					[("pickup_datetime", 1), ("pickup_borough", 1), ("pickup_zipcode", 1)],
					[("dropoff_datetime", 1), ("dropoff_borough", 1), ("dropoff_zipcode", 1)],
					[("pickup_datetime", 1), ("pickup_long_lat", "2dsphere")],
					[("dropoff_datetime", 1), ("dropoff_long_lat", "2dsphere")]],
		'collection': 'rides_15'
	}


def get_pickups_nearby_df(geocode_response, distance):
	p_rides = Ride.pickups_nearby(geocode_response[0]["geometry"]["location"]["lng"],
								  geocode_response[0]["geometry"]["location"]["lat"] , distance)
	p_rides_df = pd.DataFrame([ride.to_series() for ride in p_rides])
	p_rides_df.set_index('pickup_datetime')
	return p_rides_df


def get_dropoffs_nearby_df(geocode_response, distance):
	d_rides = Ride.dropoffs_nearby(geocode_response[0]["geometry"]["location"]["lng"],
								   geocode_response[0]["geometry"]["location"]["lat"] , distance)
	d_rides_df = pd.DataFrame([ride.to_series() for ride in d_rides])
	d_rides_df.set_index('dropoff_datetime')
	return d_rides_df