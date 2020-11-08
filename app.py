import pandas as pd
import numpy as np

import datetime as dt
from datetime import datetime
from dateutil.relativedelta import relativedelta

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

import json

# Database Setup
database_path = "../Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{database_path}?check_same_thread=False")

# Create the inspector and connect it to the engine
inspector = inspect(engine)

# Collect the names of tables within the database
inspector.get_table_names()

# Display the column names of measurement
columns = inspector.get_columns('measurement')
for column in columns:
    print(column["name"], column["type"])

# Use `engine.execute` to select and display the first 10 rows from the measurement table
engine.execute('SELECT * FROM measurement LIMIT 10').fetchall()

# Display the column names of measurement
columns = inspector.get_columns('station')
for column in columns:
    print(column["name"], column["type"])

# Use `engine.execute` to select and display the first 10 rows from the station table
engine.execute('SELECT * FROM station LIMIT 10').fetchall()

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
print(Base.classes.keys())

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)
app = Flask(__name__)

# Calculate the date 1 year ago from the last data point in the database

last_date_in_database_str = session.query(func.max(Measurement.date)).first()

print(f'Last date in the database is : {last_date_in_database_str[0]}')

# Convert to python date time object using pandas
last_date_in_database_pd = pd.to_datetime(last_date_in_database_str[0]).to_pydatetime()

# Calculate the which is one year ago from the last data point in the database
one_yr_ago_pd = last_date_in_database_pd - relativedelta(years=1)

print(f'One year ago date from the last date in the database is (in python datetime format): {one_yr_ago_pd}')

# Convert to python string object using pandas
one_yr_ago_str = pd.to_datetime(one_yr_ago_pd).strftime('%Y-%m-%d')

print(f'One year ago date from the last date in the database is (in string format): {one_yr_ago_str}')

# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

# function usage example
print(calc_temps('2012-02-28', '2012-03-05'))

# Flask Routes

@app.route("/")
def welcome():
    """List all routes that are available."""
    return ("List of Available Routes:<br/> \
            /api/v1.0/precipitation<br/> \
            /api/v1.0/stations<br/> \
            /api/v1.0/tobs<br/> \
            /api/v1.0/start/start_date<br/> \
            /api/v1.0/start/start_date/end/end_date")

@app.route("/api/v1.0/precipitation")
def dates():
    """ Return a list of all dates and temperature observations
    """
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    last_12_months_climate_db = session.query(Measurement.date, Measurement.prcp). \
                                    filter(Measurement.date.between(one_yr_ago_str, last_date_in_database_str[0])).all()

    # Save the query results as a Pandas DataFrame
    last_12_months_climate_df = pd.DataFrame( last_12_months_climate_db )

    # Clean the climate data frame by removing NaN values
    last_12_months_climate_df = last_12_months_climate_df.dropna(how='any')

    # Sort the dataframe by date
    last_12_months_climate_df = last_12_months_climate_df.sort_values(by='date')

    # Set Index
    last_12_months_climate_df.set_index(["date"], inplace=True)

    # Display to output
    last_12_months_climate_df.head()

    # Create cleaned data dictionary of the last 12 months of precipitation data
    cleaned_last_12_months_climate_dict = last_12_months_climate_df.to_dict()

    # Convert query results to dictionary
    #last_12_months_climate_list = []
    #for each_measurement in cleaned_last_12_months_climate_db:
    #    last_12_months_climate_dict = {}
    #    last_12_months_climate_dict["date"] = each_measurement.date
    #    last_12_months_climate_dict["prcp"] = each_measurement.prcp
    #    last_12_months_climate_list.append(last_12_months_climate_dict)

    # Convert list of tuples into normal list
    return jsonify(cleaned_last_12_months_climate_dict), 404

@app.route("/api/v1.0/stations")
def stations():
    # Fetch all station data
    sel = [Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]

    all_stations_db = session.query(*sel).\
                      filter(Measurement.date.between(one_yr_ago_str, last_date_in_database_str[0])).all()
    
    # Save the query results as a Pandas DataFrame
    all_stations_df = pd.DataFrame( all_stations_db )

    # Set Index
    all_stations_df.set_index(["id"], inplace=True)

    # Display to output
    all_stations_df.head()

    # Create cleaned data dictionary of the last 12 months of precipitation data
    all_stations_dict = all_stations_df.to_dict()

    #all_stations = []
    #for station in all_stations_db:
    #    station_dict = {}
    #    station_dict["station"]=all_stations_db.station
    #    all_stations.append(station_dict)

    return jsonify(all_stations_dict), 404

@app.route("/api/v1.0/tobs")
def tobs():
    # What are the most active stations? (i.e. what stations have the most rows)?
    # List the stations and the counts in descending order.

    most_active_stations_db = session.query(Measurement.station, func.count(Measurement.station)).\
                        group_by(Measurement.station).\
                        order_by(func.count(Measurement.station).desc()).all()

    print(f'Most active stations are: {most_active_stations_db}')

    # Most active station

    most_active_station_id = most_active_stations_db[0][0]
    print(most_active_station_id)

    most_active_station_name = session.query(Station.name).filter_by(station = most_active_station_id)

    for stations in most_active_station_name:
        print(f'The Most active station is: {stations[0]}')

    print(f'The Most active station name is: {most_active_station_name[0][0]}')

    # Choose the station with the highest number of temperature observations.
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    most_active_station_12_months_of_temperature_db = \
            session.query(Measurement.tobs).\
               filter(Measurement.station == most_active_station_id).\
               filter(Measurement.station == Station.station).\
               filter(Measurement.date.between(one_yr_ago_str, last_date_in_database_str[0])).all()

    most_active_station_12_months_of_temperature_df = pd.DataFrame(most_active_station_12_months_of_temperature_db)

    # Rename headers and provide cleaned name
    most_active_station_12_months_of_temperature_df = most_active_station_12_months_of_temperature_df.rename(
        columns={"tobs": f"Latest one year Temperature Observations of most active station id: {most_active_station_id} and station name {most_active_station_name[0][0]}"})
    
    most_active_station_12_months_of_temperature_dict = most_active_station_12_months_of_temperature_df.to_dict()
    #tobs_data = []
    #for tob in one_year_tobs:
        #tob_dict = {}
        #tob_dict["Temp. Observations"]= tob.tobs
        #tobs_data.append(tob_dict)

    return jsonify(most_active_station_12_months_of_temperature_dict), 404

@app.route("/api/v1.0/start/<start_date>")
def start(start_date):
    """ ✓ Route accepts the start date
        as a parameter from the URL
        ✓ Returns the min, max, and
        average temperatures
        calculated from the given start
        date to the end of the dataset"""

    # Use the function `calc_temps` to calculate the tmin, tavg, and tmax 
    # for your trip using the start date for those same dates.
    trip_start_date = start_date
    trip_end_date = last_date_in_database_str[0]

    # trip_start_date_pd = pd.to_datetime(trip_start_date).to_pydatetime()
    # trip_end_date_pd = pd.to_datetime(trip_end_date).to_pydatetime()

    #calculate the tmin, tavg, and tmax
    #last_year_start_str = pd.to_datetime(last_year_start_pd).strftime('%Y-%m-%d')
    #last_year_end_str = pd.to_datetime(last_year_end_pd).strftime('%Y-%m-%d')

    trip_temperatures = calc_temps(trip_start_date, trip_end_date)
    print(trip_temperatures)

    trip_temperatures_dict = {"My Trip Start Date": trip_start_date,
                              "My Trip End Date (Last date in database)": trip_end_date,
                              "My Trip Minimum Temperature": trip_temperatures[0][0],
                              "My Trip Maximum Temperature": trip_temperatures[0][1],
                              "My Trip average Temperature": trip_temperatures[0][2]
                              }

    return jsonify(trip_temperatures_dict), 404

@app.route("/api/v1.0/start/<start_date>/end/<end_date>")
def start_to_end(start_date, end_date):
    """ ✓ Route accepts the start and
        end dates as parameters from the URL
        ✓ Returns the min, max, and
        average temperatures
        calculated from the given start
        date to the given end date"""

    # Use the function `calc_temps` to calculate the tmin, tavg, and tmax 
    # for your trip using the start date for those same dates.
    trip_start_date = start_date
    trip_end_date = end_date

    # trip_start_date_pd = pd.to_datetime(trip_start_date).to_pydatetime()
    # trip_end_date_pd = pd.to_datetime(trip_end_date).to_pydatetime()

    #calculate the tmin, tavg, and tmax
    #last_year_start_str = pd.to_datetime(last_year_start_pd).strftime('%Y-%m-%d')
    #last_year_end_str = pd.to_datetime(last_year_end_pd).strftime('%Y-%m-%d')

    trip_temperatures = calc_temps(trip_start_date, trip_end_date)
    print(trip_temperatures)

    trip_temperatures_dict = {"My Trip Start Date": trip_start_date,
                              "My Trip End Date (Last date in database)": trip_end_date,
                              "My Trip Minimum Temperature": trip_temperatures[0][0],
                              "My Trip Maximum Temperature": trip_temperatures[0][1],
                              "My Trip average Temperature": trip_temperatures[0][2]
                              }
    trip_temperatures_json = json.dumps(trip_temperatures_dict, sort_keys=True, indent=1)

    #return trip_temperatures_json, 404
    return jsonify(trip_temperatures_dict), 404

if __name__ == "__main__":
    app.run(debug=True)
