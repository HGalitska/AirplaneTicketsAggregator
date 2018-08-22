import requests
import json

class WizzairInfoRobber:
    def getFlights(self, depart, arrive, date):
        people = '1'
        data = {"isFlightChange":'false',"isSeniorOrStudent":'false',
                                    "flightList":[{"departureStation":depart,"arrivalStation":arrive,"departureDate":date}],
                                    "adultCount":people,"childCount":'0',"infantCount":'0',"wdc":'true'}
        r = requests.post(url="https://be.wizzair.com/8.2.1/Api/search/search",
                          json=data,
                          headers={"content-type": "application/json;charset=UTF-8"})
        if r.status_code == 200:
            json_response = json.loads(r.text)
            flights = json_response['outboundFlights']
            results = []
            for flight in flights:
                json_flight = {}
                json_flight['airportA'] = depart
                json_flight['airportB'] = arrive
                json_flight['airline'] = 'Wizzair'
                json_flight['date'] = flight['departureDateTime']
                fares = flight['fares']
                for fare in fares:
                    if fare['bundle'] == 'BASIC' and not fare['wdc']:
                        full_price = fare['fullBasePrice']
                        json_flight['price'] = full_price['amount']
                results.append(json_flight)
            return results
        return None
