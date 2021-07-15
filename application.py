import json
import schedule
import threading
import logging
import os.path
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from utilities.weather import OpenWeatherHandler
from utilities.smartplug import SmartPlugHandler

app = Flask(__name__)
Bootstrap(app)

appSettings = None
smartPlugHandler = None
openWeatherHandler = None

HOURS_FOR_WEATHER_CALCULATION = 8
WATERING_INTENSITY_LEVEL_HIGH = 3
WATERING_INTENSITY_LEVEL_MEDIUM = 2
WATERING_INTENSITY_LEVEL_LOW = 1
WATERING_INTENSITY_LEVEL_NONE = 0

RAINING_DAY_BEFORE = False

@app.route("/")
def index():
    value = smartPlugHandler.isOnline
    logging.info(value)
    return render_template('index.html')

@app.route("/logs")
@app.route("/logs/<int:amountlines>")
def logs(amountlines=None):
    log_filename = "app_smartwateringsystem.log"
    if not os.path.isfile(log_filename):
        return "No log file found."
    
    if (amountlines is not None):
        amountlines = 0 - amountlines
    else:
        amountlines = -100
    
    log_file = open(log_filename, "r")
    lines = log_file.readlines()
    log_file.close()
    last_lines = lines[amountlines:]
    result = "<br>".join(last_lines)
    return result


def initSettings():
    if not os.path.isfile("settings.json"):
        raise Exception('Missing configuration file `settings.json`. Please create this with `settings_example.json`.')
    
    settings_file = open('settings.json')
    settings = json.load(settings_file)
    settings_file.close()

    global appSettings
    appSettings = settings

def initLogging():
    logLevel = logging.getLevelName(appSettings["Logging"]["LogLevel"])
    if "LOCAL" in appSettings["Environment"]:
        logging.basicConfig(level=logLevel)
        logging.info('Configure local logging finisehd.')
        return

    if "LogFile" in appSettings["Logging"] and appSettings["Logging"]["LogFile"]:
        logging.basicConfig(filename=appSettings["Logging"]["LogFile"], level=logLevel)
    logging.info('Configure logging finisehd.')

def initWeatherHandler():
    global openWeatherHandler
    openWeatherHandler = OpenWeatherHandler()
    openWeatherHandler.init(appSettings["OpenWeather"])
    openWeatherHandler.loadWeatherData()
    logging.info('Configure weather handler finished.')

def initSmartPlugHandler():
    global smartPlugHandler
    smartPlugHandler = SmartPlugHandler(appSettings["SmartPlug"]["IpAddress"])
    logging.info('Configure smart plug handler finished.')

    smartPlugHandler.turnOff() # turn off initial

def startScheduler():
    startAt = appSettings["Watering"]["TimeForWatering"]

    logging.info('Initialize scheduler with start time %s' % (startAt))

    schedule.every().day.at(startAt).do(handleWatering)

    while 1:
        schedule.run_pending()

def emitWaterIntesity(averageProbabilityOfRain, averageTemperature):
    if RAINING_DAY_BEFORE and averageTemperature < 30:
        return WATERING_INTENSITY_LEVEL_NONE

    if averageProbabilityOfRain <= 20:
        return WATERING_INTENSITY_LEVEL_MEDIUM
    elif 20 < averageProbabilityOfRain <= 60:
        return WATERING_INTENSITY_LEVEL_LOW
    elif averageProbabilityOfRain > 60:
        return WATERING_INTENSITY_LEVEL_NONE

def handleWatering():
    global RAINING_DAY_BEFORE
    logging.info("Start handle watering.")

    openWeatherHandler.loadWeatherData()
    if openWeatherHandler._wantedWeatherData == None:
        logging.info("No weahter data was found.")
        return

    averageProbabilityOfRain = openWeatherHandler.getAverageProbabilityOfRain()
    averageTemperature = openWeatherHandler.getAverageTemperature(8)

    wateringDuration = appSettings["Watering"]["WateringDurationInSeconds"]
    delayBetweenWatering = appSettings["Watering"]["DelayBetweenWateringInSeconds"]

    logging.info("Average probability of rain: %s." % (averageProbabilityOfRain))
    logging.info("Average temperatur: %s." % (averageTemperature))

    waterIntensity = emitWaterIntesity(averageProbabilityOfRain, averageTemperature)
    logging.info("Repeat watering with intesity of %s  watering duration %s and delay %s." % (waterIntensity, wateringDuration, delayBetweenWatering))
    smartPlugHandler.repeat(waterIntensity, wateringDuration, delayBetweenWatering)
    
    RAINING_DAY_BEFORE = openWeatherHandler.isRainingToday()

initSettings()
initLogging()
schedulerThread = threading.Thread(target=startScheduler)  
schedulerThread.start()

initWeatherHandler()
initSmartPlugHandler()

if __name__ == '__main__':
    app.run(host="localhost", port=28200, debug=True, use_reloader=True)
        