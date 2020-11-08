#################################################
# MongoDB and Flask Application
#################################################

# Dependencies and Setup
from flask import Flask, render_template
from flask_pymongo import PyMongo
import scrape_mars

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Mac
#################################################
# Set Executable Path & Initialize Chrome Browser

#def init_browser():
    #executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    #return Browser("chrome", **executable_path, headless=False)

#################################################
# Windows
#################################################
# Set Executable Path & Initialize Chrome Browser

def init_browser():
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)

#################################################
# PyMongo Connection Setup
#################################################
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_db"
mongo = PyMongo(app)

#################################################
# Flask Routes
#################################################
# Root Route to Query MongoDB & Pass Mars Data Into HTML Template: index.html to Display Data
@app.route("/")
def index():
    mars = mongo.db.mars.find_one()
    print(mars)
    return render_template("index.html", mars=mars)

# Scrape Route to Import `scrape_mars.py` Script & Call `scrape` Function
@app.route("/scrape")
def scrapper():
    mars = mongo.db.mars
    mars_data = scrape_mars.scrape_all()
    mars.update({}, mars_data, upsert=True)

    return "Scraping Successful! Hit Back Button Now to view data"

# Define Main Behavior
if __name__ == "__main__":
    app.run(debug=True)
