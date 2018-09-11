from app import arangodb

class AirlinesManager:
    def increase_count(self, airline, date):
        print("in increase")
        print(date)
        airlines = arangodb.collection('airlines_data')
        if airlines.has(airline.lower()):
            airline_data = airlines.get(airline.lower())
            date_parts = date.split('-')
            if len(date_parts) == 3:
                year = "year_" + date_parts[0]
                month = int(date_parts[1])
                stats = airline_data['stats']
                year_object = stats[year]
                if year_object is None:
                    stats[year] = {"counters" : [0] * 12}
                    airlines.update(airline_data)
                    year_object = stats[year]
                months = year_object['counters']
                months[month - 1] = months[month - 1] + 1
                year_object['counters'] = months
                airlines.update(airline_data)



