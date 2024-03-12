# Import the dependencies.
import numpy as np
import datetime as dt

#import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create the engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
Session = Session(bind=engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# MAIN HOME ROUTE
@app.route("/")
def home():
    return (
        f"Welcome to Jasleen's Hawaii API <br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start> and /api/v1.0/<start>/<end>"
    )

# PERCIPITATION ROUTE
@app.route("/api/v1.0/precipitation")
def rain_route():
    prev_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    results = Session.query(measurement.date, measurement.prcp).filter(measurement.date >= prev_year).all()

    Session.close()

    precipitation_list = []

    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        precipitation_list.append(prcp_dict)

    return jsonify(precipitation_list)

# STATIONS ROUTE
@app.route("/api/v1.0/stations")
def stations_route():
    
    active_stations = Session.query(measurement.station, 
   func.count(measurement.station)).group_by(measurement.station).\
      order_by(func.count(measurement.station).desc()).all()

    Session.close()

    station_list = []

    for station in active_stations:
       station_names = {
           "station": station[0],
           "count": station[1]
       }
       station_list.append(station_names)

    return jsonify(station_list)

# TEMPERATURE ROUTE
@app.route("/api/v1.0/tobs")
def temperature():

    prev_year = dt.date(2017,8,23) - dt.timedelta(days=365)

    most_active_station_id = "USC00519281"
    
    temperature_data = Session.query(measurement.tobs).filter(
    measurement.station == most_active_station_id,
    measurement.date >= prev_year).all()

    Session.close()

    temp_list = list(np.ravel(temperature_data))

    return jsonify(temp_list)

# START & START / END ROUTE
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")

def start_end_route(start, end=None):
    
    start = dt.datetime.strptime(start, "%Y%m%d")
    print("*********************************************")
    print(start)

    if not end:
        final_list = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
        results = Session.query(*final_list).filter(measurement.date >= start).all()
        Session.close()
        final_list = list(np.ravel(results))
        return jsonify(final_list)
    
    else:
        end = dt.datetime.strptime(end, "%Y%m%d")
        final_list = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
        results = Session.query(*final_list).filter(measurement.date >= start, measurement.date <= end).all()
        Session.close()
        final_list = list(np.ravel(results))
        return jsonify(final_list)
    

if __name__ == "__main__":
    app.run(debug=True)