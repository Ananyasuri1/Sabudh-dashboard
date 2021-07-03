from os import name
import flask
from flask import Flask, render_template, request
import requests
import pandas as pd
import plotly
import plotly.express as px
import json


# Create Flask's `app` object
app = Flask(
    __name__,
    template_folder="templates"
)
district = {'sangrur' : 'IN0008B.csv', 'amritsar' : "IN0238B.csv", 'kapurthala' : "IN0239B.csv", 'jalandhar' : "IN0240B.csv", 'ferozepur' : "IN0247B.csv", 'bhatinda' : "IN0248B.csv", 'ludhiana' : "IN0249B.csv", 'patiala' : "IN0250B.csv", 'chandigarh' : "IN0666B.csv"}
def tocelcius(temp):
    return str(round(float(temp) - 273.16,2))
def plotgraph(city,sdate,edate) :
    str1 = 'static/csv/'
    str2 = str(district[city])
    path = str1 + str2
    print(path)
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'])
    mask = (df['date'] >= sdate) & (df['date'] <= edate)
    df = df.loc[mask]
    temperature = px.line(df, x="date", y="max", labels={ "date": "Year", "max": "Maximum Temperature(C)",})
    maxspeed = px.line(df, x = 'date', y = "min", labels={ "date": "Year", "min": "Minimum Temperature(C)",})
    precip = px.line(df, x='date', y='mxspd', labels={ "date": "Year", "mxspd": "WindSpeed(km/h)",})
    tempJSON = json.dumps(temperature, cls=plotly.utils.PlotlyJSONEncoder)
    mxspdJSON = json.dumps(maxspeed, cls=plotly.utils.PlotlyJSONEncoder)
    prcpJSON = json.dumps(precip, cls=plotly.utils.PlotlyJSONEncoder)
    return tempJSON,mxspdJSON,prcpJSON

def forecastplot(city,sdate,edate) :
    str1 = 'static/csv/'
    str2 = str(district[city])
    path = str1 + str2
    print(path)
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'])
    mask = (df['date'] >= sdate)
    df = df.loc[mask]
    print(df['max'])
    dfmax = pd.read_csv('static/csv/tempmax.csv')
    dfmin = pd.read_csv('static/csv/tempmin.csv')
    dfspd = pd.read_csv('static/csv/speed.csv')
    dfmax['date'] = pd.to_datetime(dfmax['date'])
    mask1 = (dfmax['date'] >= sdate)
    dfmax = dfmax.loc[mask1]
    dfmin['date'] = pd.to_datetime(dfmin['date'])
    mask2 = (dfmin['date'] >= sdate)
    dfmin = dfmin.loc[mask2] 
    dfspd['date'] = pd.to_datetime(dfspd['date'])
    mask3 = (dfspd['date'] >= sdate)
    dfspd = dfspd.loc[mask3]       
    data = [dfmax['date'],df['max'],df['min'],df['mxspd'],dfmax['max'],dfmin['min'],dfspd['mxspd']]
    headers = ["date","Maximum Temp","Minimum Temp","WindSpeed","Forecasted Max Temp","Forecasted Min Temp","Forecasted WindSpeed"]
    finaldf = pd.concat(data, axis=1, keys=headers)
    print(finaldf.head())
    temperature = px.line(df, x="date", y='max',)
    maxspeed = px.line(df, x = 'date', y ='min', )
    precip = px.line(df, x='date', y='mxspd',)
    temperature.add_scatter(x=finaldf['date'],y=finaldf['Forecasted Max Temp'])
    maxspeed.add_scatter(x=finaldf['date'],y=finaldf['Forecasted Min Temp'])
    precip.add_scatter(x=finaldf['date'],y=finaldf['Forecasted WindSpeed'])
    temperature.update_layout(
    xaxis_title="Year",
    yaxis_title="Maximum Temperature (C)",
    )
    maxspeed.update_layout(
    xaxis_title="Year",
    yaxis_title="Minimum Temperature (C)",
    )
    precip.update_layout(
    xaxis_title="Year",
    yaxis_title="WindSpeed (km/h)"
    )
    tempJSON = json.dumps(temperature, cls=plotly.utils.PlotlyJSONEncoder)
    mxspdJSON = json.dumps(maxspeed, cls=plotly.utils.PlotlyJSONEncoder)
    prcpJSON = json.dumps(precip, cls=plotly.utils.PlotlyJSONEncoder)
    return tempJSON,mxspdJSON,prcpJSON

def weatherapi(city,sdate,edate):
    try:
        url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid=48a90ac42caa09f90dcaeee4096b9e53'
        source = requests.get(url.format(city)).json()
    except:
        return None
    # converting json data to dictionary

    # data for variable list_of_data
    data = {
        "temp_cel" : tocelcius(source['main']['temp']) + ' C',
        "humidity" : str(source['main']['humidity']) + " %",
        "cityname" : city.upper(),
        "speed" : str(source['wind']['speed']) + ' km/h',
        "pressure" : str(source['main']['pressure']),
        "startdate" : sdate,
        "enddate" : edate

    }
    return data

city = 'chandigarh'

@app.route("/" , methods = ['POST', 'GET'])
def index():
    global city
    if request.method == 'POST' :
        city =  request.form['city']
    else :
        city = 'chandigarh'

    data = weatherapi(city,sdate = "1957-01-03",edate="2020-12-10")
    # Ploting graphs
    tempJSON,mxspdJSON,prcpJSON = plotgraph(city,sdate = "1957-01-03",edate="2020-12-10")
    return render_template('index.html',data=data, temp = tempJSON, spd = mxspdJSON, prcp = prcpJSON)

@app.route("/dataselect" , methods = ['POST', 'GET'])
def dataselect() :
    global city
    if request.method == 'POST' :
        sdate = request.form['startdate']
        edate = request.form['enddate']
    data = weatherapi(city,sdate,edate)
    tempJSON,mxspdJSON,prcpJSON = plotgraph(city,sdate,edate)
    return render_template('index.html', data=data,temp = tempJSON, spd = mxspdJSON, prcp = prcpJSON)

@app.route("/dataforecast" , methods = ['POST', 'GET'])
def dataforecast() :
    global city
    if request.method == 'POST' :
        sdate = "2020-01-01"
        edate = "2020-12-31"
    data = weatherapi(city,sdate,edate)
    tempJSON,mxspdJSON,prcpJSON = forecastplot(city,sdate,edate)
    return render_template('index.html', data=data,temp = tempJSON, spd = mxspdJSON, prcp = prcpJSON)
@app.route('/charts')
def charts():
	return render_template('charts.html')

@app.route('/tables')
def tables():
	return render_template('tables.html')