# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func,inspect

from flask import Flask, jsonify



#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
inspector = inspect(engine)
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        # f"By start_date: YYYY-MM-DD<br/>"
        # f"<br/>"
        # f"/api/v1.0/start_date/YYYY-MM-DD/<br/>"
        # f"<br/>"
        # f"By start_date/end_date: YYYY-MM-DD/YYYY-MM-DD<br/>"
        # f"<br/>"
        # f"/api/v1.0/start_date/YYYY-MM-DD/end_date/YYYY-MM-DD"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    # session = Session(engine)
    print("hello1")
    """Return a list of all passenger names"""
    # Query all passengers
    # results = session.query(Passenger.name).all()

    # session.close()

    # # Convert list of tuples into normal list
    # all_names = list(np.ravel(results))

    # return jsonify(all_names)
    return "Precipitation"



@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    session.close()

    stations = list(np.ravel(results))

    return jsonify(stations)



@app.route("/api/v1.0/tobs")
def tobs():
    print("hello3")


    return "temperature observations"



# @app.route("/api/v1.0/start_date/<YYYY-MM-DD>")
# def start_date(start_date):

#     print("hello4")

#     return "start date"



# @app.route("/api/v1.0/start_date/<YYYY-MM-DD>/end_date/<YYYY-MM-DD>")
# def start_end_date(start_date,end_date):

#     print("hello5")

#     return "start date and end date"


if __name__ == '__main__':
    app.run(debug=True)
