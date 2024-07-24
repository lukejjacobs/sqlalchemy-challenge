# Import the dependencies.
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from datetime import datetime
import dateutil.parser as parser
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite+pysqlite:///SurfsUp/Resources/hawaii.sqlite")

# reflect an existing database into a new model

model = automap_base()

# reflect the tables

model.prepare(autoload_with = engine)

# Save references to each table
Meas = model.classes.measurement
Station = model.classes.station

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
def home_route():
    """List all available api routes."""
    return (
        f"Welcome to the landing page of my Hawaii data website!<br/>" 
        f"<br/>" 
        f"Here are the Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start=YYYY-MM-DD<start><br/>"
        f"/api/v1.0/start=YYYY-MM-DD<start>/end=YYYY-MM-DD<end><br/>"
        f"<br/>"
        f"Please note: For the dates, you must enter the date in the format Year-Month-Day.<br/>"
        f"Example: 2016-04-18."
    )


@app.route("/api/v1.0/precipitation")
def precipitation_route():
    session = Session(engine)
    recent_date = (session.query(Meas.date).order_by(Meas.date.desc()).first())
    year = datetime.strptime(recent_date[0], "%Y-%m-%d").date() - dt.timedelta(days=365)
    results = (session.query(Meas).filter(Meas.date >= year).order_by(Meas.date).all())
    session.close()
    data_dic = {row.date: row.prcp for row in results}
    return jsonify(data_dic)


@app.route("/api/v1.0/stations")
def stations_route():
    session = Session(engine)
    results = session.query(Station).all()
    session.close()
    data_dic = {'Stations':[row.station for row in results]}
    return jsonify(data_dic)


@app.route("/api/v1.0/tobs")
def tobs_route():
    session = Session(engine)
    active_id = (session.query(Meas.station, func.count(Meas.station)).group_by(Meas.station).order_by(func.count(Meas.station).desc()).all()[0][0])
    recent_date = (session.query(Meas.date).filter(Meas.station == active_id).order_by(Meas.date.desc()).first())
    year = datetime.strptime(recent_date[0], "%Y-%m-%d").date() - dt.timedelta(days=365)
    results = (session.query(Meas).filter(Meas.date >= year).order_by(Meas.date).all())
    session.close()
    temp_dic = {'Temperatures' : [row.tobs for row in results]}
    return jsonify(temp_dic)


@app.route("/api/v1.0/start=<start>")
def start_route(start):
    start = parser.parse(start).date()
    session = Session(engine)
    results = (session.query(func.min(Meas.tobs),func.max(Meas.tobs),func.sum(Meas.tobs) / func.count(Meas.tobs),).filter(Meas.date >= start).all())
    session.close()
    stats_dic = {"Min": results[0][0],"Max": results[0][1],"Avg": results[0][2],}
    return jsonify(stats_dic)


@app.route("/api/v1.0/start=<start>/end=<end>")
def start_end_route(start, end):
    start = parser.parse(start).date()
    end = parser.parse(end).date()
    if start > end:
        beginning_date = end
        ending_date = start
    else:
        beginning_date = start
        ending_date = end
    session = Session(engine)
    results = (session.query(func.min(Meas.tobs),func.max(Meas.tobs),func.sum(Meas.tobs) / func.count(Meas.tobs),).filter((Meas.date >= beginning_date) & (Meas.date <= ending_date)).all())
    session.close()
    stats_dic = {"Min": results[0][0],"Max": results[0][1],"Avg": results[0][2],}
    return jsonify(stats_dic)


if __name__ == "__main__":
    app.run(debug=True)