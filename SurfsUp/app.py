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
        f"By start_date using format: /api/v1.0/YYYY-MM-DD/<br/>"
        f"<br/>"
        f"/api/v1.0/2016-02-12<br/>"
        f"<br/>"
        f"By start_date/end_date using format: /api/v1.0/YYYY-MM-DD/YYYY-MM-DD<br/>"
        f"<br/>"
        f"/api/v1.0/2016-03-17/2017-01-12"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent = dt.date(2017, 8, 23)    
    one_year = most_recent - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year).all()
    session.close()

    precipitation = {}
    for date, prcp in results:
        precipitation[date] = prcp

    return jsonify(precipitation)



@app.route("/api/v1.0/stations")
def stations():


    results = session.query(Station.station).all()
    session.close()

    stations = list(np.ravel(results))

    return jsonify(stations)



@app.route("/api/v1.0/tobs")
def temperature_observations():

    station_id = session.query((Measurement.station.distinct()),func.count(Measurement.station)).\
    group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    most_recent = dt.date(2017, 8, 23)    
    one_year = most_recent - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= one_year).\
        filter(Measurement.station == station_id).all()
    session.close()

    temperature_observations = {}
    for date, tobs in results:
        temperature_observations[date] = tobs

    return jsonify(temperature_observations)


@app.route("/api/v1.0/<start_date>")
def start_date(start_date):

    # format = '%Y-%m-%d'
    # date = dt.datetime.strptime(start_date, format).date()
    
    # station_id = session.query((Measurement.station.distinct()),func.count(Measurement.station)).\
    #     group_by(Measurement.station).\
    #         order_by(func.count(Measurement.station).desc()).first()[0]


    stats = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()\
            # filter(Measurement.station == station_id).all()
    session.close()

    stats_dict = {
        "start_date":start_date,
        "TMIN":stats[0][0],
        "TMAX":stats[0][1],
        "TAVG":stats[0][2]
        }

    return jsonify(stats_dict)


@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end_date(start_date,end_date):

    # format = '%Y-%m-%d'
    # date_1 = dt.datetime.strptime(start_date, format).date()
    # date_2 = dt.datetime.strptime(end_date, format).date()
    
    # station_id = session.query((Measurement.station.distinct()),func.count(Measurement.station)).\
    #     group_by(Measurement.station).\
    #         order_by(func.count(Measurement.station).desc()).first()[0]


    stats = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()\
            # filter(Measurement.station == station_id).all()
    session.close()

    stats_dict = {
        "start_date":start_date,
        "end_date":end_date,
        "TMIN":stats[0][0],
        "TMAX":stats[0][1],
        "TAVG":stats[0][2]
        }
    
    return jsonify(stats_dict)


if __name__ == '__main__':
    app.run(debug=True)
