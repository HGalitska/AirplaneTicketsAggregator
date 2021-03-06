from app import arangodb
import datetime


class SavedFlightsManager:
    def init_flight(self, flight_id, user_id):

        saved_flights = arangodb.collection('saved_flights')
        # if not saved_flights.has(str(flight_id)):
        # first user who saved the flight
        flight = {"_key": str(flight_id), 'flight_id': flight_id, "users": [user_id]}
        saved_flights.insert(flight)

    def add_saved_flight(self, flight_id, user_id, fares):
        saved_flights = arangodb.collection('saved_flights')
        flights_stats = arangodb.collection('flights_stats')

        if not saved_flights.has(str(flight_id)):
            self.init_flight(flight_id, user_id)
        else:
            saved_flight = saved_flights.get(str(flight_id))
            users = saved_flight['users']

            # надо ли?
            if user_id not in users:
                users.append(user_id)
                saved_flight['users'] = users
                saved_flights.update(saved_flight)

        if not flights_stats.has(str(flight_id)):
            stats = {"_key": str(flight_id), 'prices': [{'date': str(datetime.date.today()), 'fares': fares}], }
            flights_stats.insert(stats)
        # по идее, если уже есть полет, то цены будет обновлять flights updater
