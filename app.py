from flask import Flask, render_template
import requests
import json


# Create Flask's `app` object
app = Flask(
    __name__,
    template_folder="templates"
)
def tocelcius(temp):
    return str(round(float(temp) - 273.16,2))

@app.route("/")
def index():

    city = 'chandigarh'

    # source contain json data from api
    try:
        url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid=48a90ac42caa09f90dcaeee4096b9e53'
        source = requests.get(url.format(city)).json()
    except:
        return None
    # converting json data to dictionary

    # data for variable list_of_data
    data = {
        "temp_cel" : tocelcius(source['main']['temp']) + 'C',
        "humidity" : source['main']['humidity'],
        "cityname" : city,
        "temp_min" : tocelcius(source['main']['temp_min']) + 'C',
        "temp_max" : tocelcius(source['main']['temp_max']) + 'C',
    }
    return render_template('index.html',data=data)

@app.route('/charts')
def charts():
	return render_template('charts.html')

@app.route('/tables')
def tables():
	return render_template('tables.html')