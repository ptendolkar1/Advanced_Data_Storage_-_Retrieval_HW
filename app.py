from flask import Flask, jsonify

from datetime import date, time, datetime, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
# Create an engine to a SQLite database file called `hawaii.sqlite`
engine = create_engine("sqlite:///hawaii.sqlite")

# Declare a Base using `automap_base()` 
# i.e. assign Base the automap functionality
Base = automap_base()

# Use the Base class to reflect the database tables 
# from engine. Automap base converts tables to classes automatically 
Base.prepare(engine, reflect=True)

# Reflect tables into classes and save references to 
# those classes called `Station` and `Measurement`. 
Measurements = Base.classes.measurements
Stations = Base.classes.stations

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List of available api routes."""
    return (
        f"Available api Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<'start'>    Note: append dates as YYYY-MM-DD <br/>"
        f"/api/v1.0/<'start'>/<'end'>    Note: append dates as YYYY-MM-DD"
    )

#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return json representation of the dictionary of dates and tobs"""
    sel = [Measurements.date, Measurements.tobs]
    tobs12_data = session.query(*sel).\
        filter(func.strftime("%YY/%m/%d", Measurements.date) >= "2016/08/01").all()  
    # Available data is upto August 2018 only, so 12 months from Aug 2016 to Aug 2017 considered.
    # Convert tobs12_data into dictionary
    tobs12_dict = dict(tobs12_data)
    return jsonify(tobs12_dict)

#################################################

@app.route("/api/v1.0/stations")
def stations():

    sel = [Stations.station, Stations.name]
    List_of_stations = session.query(*sel).\
        filter(Stations.station == Measurements.station).\
        group_by(Measurements.station).all()

    return jsonify(List_of_stations)

#################################################
# Return a json list of Temperature Observations (tobs) for the previous year

@app.route("/api/v1.0/tobs")
def tobs():

    sel = [Measurements.date, Measurements.tobs]
    tobs_previous_year = session.query(*sel).\
    filter(func.strftime("%YY/%m/%d", Measurements.date) >= "2015/08/01").\
    filter(func.strftime("%YY/%m/%d", Measurements.date) <= "2016/08/01").all()
    # Convert tobs12_data into dictionary
    tobs_previous_year_dict = dict(tobs_previous_year)

    return jsonify(tobs_previous_year_dict)

#################################################

@app.route("/api/v1.0/<start>") 
def tobs_since(start):

    tobs_since = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
    filter(Measurements.date >= start).all()

    tobs_since_list = list(np.ravel(tobs_since))

    return jsonify(tobs_since_list)

#################################################

@app.route("/api/v1.0/<start>/<end>") 
def tobs_range(start, end):

    """Return a json list of min, avg, and max temperatures between 2 dates."""
    
    tobs_range = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
    filter(Measurements.date >= start).filter(Measurements.date <= end).all()

    tobs_range_list = list(np.ravel(tobs_range))

    return jsonify(tobs_range_list)

#################################################

if __name__ == "__main__":
    app.run(debug=True)