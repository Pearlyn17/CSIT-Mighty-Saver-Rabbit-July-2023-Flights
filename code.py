from pymongo import MongoClient
from datetime import datetime
import flask

# Connect to MongoDB
client = MongoClient('mongodb+srv://userReadOnly:7ZT817O8ejDfhnBM@minichallenge.q4nve1r.mongodb.net/')

database = client['minichallenge']

flightsdb = database['flights']
hotelsdb = database['hotels']

# Get a list of return flights at the cheapest price, given the destination city, departure date, and arrival date.
def GetFlight(destcity, arrivaldate, departuredate):

    flightinfo = {
        "City": destcity,                   #destcity
        "Departure Date": arrivaldate,      #date
        "Return Date": departuredate,       #date
        }

    for depatureflight in flightsdb.find({"srccity": "Singapore", "date": datetime.strptime(arrivaldate, '%Y-%m-%d'), "destcity": destcity}).sort("price").limit(1):                 # Get Depature Flight
        flightinfo["Departure Airline"] = depatureflight.get("airlinename")
        flightinfo["Departure Price"] = depatureflight.get("price")

    for returnflight in flightsdb.find({"srccity": destcity, "date": datetime.strptime(departuredate, '%Y-%m-%d'), "destcity": "Singapore"}).sort("price").limit(1):                 # Get Return Flight
        flightinfo["Return Airline"] = returnflight.get("airlinename")
        flightinfo["Return Price"] = returnflight.get("price")

    if flightinfo.get("Departure Airline") == None or flightinfo.get("Return Airline") == None:
        return []

    return [flightinfo]

# Get a list of hotels providing the cheapest price, given the destination city, check-in date, and check-out date.
def GetHotel(city, checkindate, checkoutdate):

    hotelinfo = {
        "City": city,                         #city
        "Check In Date": checkindate,         #date
        "Check Out Date": checkoutdate,       #date
    }

    hotelscost = {}

    for hotel in hotelsdb.find({"city": city, "date": { "$gte": datetime.strptime(checkindate, '%Y-%m-%d'), "$lte": datetime.strptime(checkoutdate, '%Y-%m-%d') }}):         # Get Hotel
        if hotel.get("hotelName") in hotelscost:
            currentpricing = hotelscost[hotel.get("hotelName")]
            hotelscost[hotel.get("hotelName")] = currentpricing + hotel.get("price")
        else:
            hotelscost[hotel.get("hotelName")] = hotel.get("price")

    if len(hotelscost) >= 1:
        cheapest = min(hotelscost.values())
        for hotel in hotelscost:
            if hotelscost[hotel] == cheapest:
                hotelinfo["Hotel"] = hotel
                hotelinfo["Price"] = cheapest

    if hotelinfo.get("Hotel") == None:
        return []
    
    return [hotelinfo]

# Flask Server
app = flask.Flask(__name__)

@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello World'

@app.route('/flight', methods=['GET'])
def getflight():
    try:
        args = flask.request.args
        departureDate = args.get("departureDate", default="", type=str)
        returnDate = args.get("returnDate", default="", type=str)
        destination = args.get("destination", default="", type=str)
        if departureDate == "" or returnDate == "" or destination == "":
            return "Bad input.", 400
        elif datetime.strptime(departureDate, '%Y-%m-%d') > datetime.strptime(returnDate, '%Y-%m-%d'):
            return "Bad input.", 400
        elif datetime.strptime(departureDate, '%Y-%m-%d') < datetime.now():
            return "Bad input.", 400
        elif datetime.strptime(returnDate, '%Y-%m-%d') < datetime.now():
            return "Bad input.", 400
        return GetFlight(destination, departureDate, returnDate)
    except:
        return "Bad input.", 400

@app.route('/hotel', methods=['GET'])
def gethotel():
    try: 
        args = flask.request.args
        checkInDate = args.get("checkInDate", default="", type=str)
        checkOutDate = args.get("checkOutDate", default="", type=str)
        destination = args.get("destination", default="", type=str)
        if checkInDate == "" or checkOutDate == "" or destination == "":
            return "Bad input.", 400
        elif datetime.strptime(checkInDate, '%Y-%m-%d') > datetime.strptime(checkOutDate, '%Y-%m-%d'):
            return "Bad input.", 400
        elif datetime.strptime(checkInDate, '%Y-%m-%d') < datetime.now():
            return "Bad input.", 400
        elif datetime.strptime(checkOutDate, '%Y-%m-%d') < datetime.now():
            return "Bad input.", 400
        return GetHotel(destination, checkInDate, checkOutDate)
    except:
        return "Bad input.", 400

# main driver function
if __name__ == '__main__':
   
    app.run()
