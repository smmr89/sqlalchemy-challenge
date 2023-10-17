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
        f"/api/v1.0/precipitation - last 12 months of precipitation data<br/>"
        f"/api/v1.0/stations - a list of all stations<br/>"
        f"/api/v1.0/tobs - a list of tempertaure observations from the most active station of the previous year<br/>"
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

    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    format = '%Y-%m-%d'
    most_recent = dt.datetime.strptime(most_recent[0], format).date()

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

    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    format = '%Y-%m-%d'
    most_recent = dt.datetime.strptime(most_recent[0], format).date()

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

    format = '%Y-%m-%d'

    try:
        date1 = dt.datetime.strptime(start_date, format).date()
    except ValueError:
        session.close()
        error_msg = f"User date input '{start_date}' does not match format 'YYYY-MM-DD'"
        return jsonify({"error": error_msg}), 404
    
    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent = dt.datetime.strptime(most_recent[0], format).date()

    if date1 > most_recent:
        session.close()
        return jsonify({"error": f"The most recent date with available data is '{most_recent}'. Try with an earlier date"}), 404

    stats = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= date1).all()

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

    format = '%Y-%m-%d'

    try:
        date1 = dt.datetime.strptime(start_date, format).date()
    except ValueError:
        session.close()
        error_msg = f"User date input '{start_date}' does not match format 'YYYY-MM-DD'"
        return jsonify({"error": error_msg}), 404
    
    try:
        date2 = dt.datetime.strptime(end_date, format).date()
    except ValueError:
        session.close()
        error_msg = f"User date input '{end_date}' does not match format 'YYYY-MM-DD'"
        return jsonify({"error": error_msg}), 404


    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent = dt.datetime.strptime(most_recent[0], format).date()


    most_earliest = session.query(Measurement.date).order_by(Measurement.date).first()
    most_earliest = dt.datetime.strptime(most_earliest[0], format).date()

    if date1 >= date2:
        session.close()
        return jsonify({"error": f"End Date cannot be earlier than or the same as the Start Date"}), 404
    


    if date2 < most_earliest:
        session.close()
        return jsonify({"error": f"The earliest date with available data is '{most_earliest}'. Try with an End Date equal to later than that"}), 404



    if date1 > most_recent:
        session.close()
        return jsonify({"error": f"The most recent date with available data is '{most_recent}'. Try with a Start Date equal to earlier than that"}), 404



    stats = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

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
