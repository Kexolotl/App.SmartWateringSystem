import json
import schedule
import threading
import logging
import os.path
from flask import Flask, render_template
from utilities.weather import OpenWeatherHandler
from utilities.smartplug import SmartPlugHandler

app = Flask(__name__)

appSettings = None
smartPlugHandler = None
openWeatherHandler = None

HOURS_FOR_WEATHER_CALCULATION = 8
WATERING_INTENSITY_LEVEL_HIGH = 3
WATERING_INTENSITY_LEVEL_MEDIUM = 2
WATERING_INTENSITY_LEVEL_LOW = 1

@app.route("/")
def index():
    value = smartPlugHandler.isOnline
    logging.info(value)
    return render_template('index.html')

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
    smartPlugHandler.connect()
    logging.info('Configure smart plug handler finished.')

    smartPlugHandler.turnOff() # turn off initial

def startScheduler():
    startAt = appSettings["Watering"]["TimeForWatering"]

    logging.info('Initialize scheduler with start time %s' % (startAt))

    schedule.every().day.at(startAt).do(handleWatering)

    while 1:
        schedule.run_pending()

def handleWatering():
    logging.info("Start handle watering.")
    averageProbabilityOfRain = openWeatherHandler.getAverageProbabilityOfRain(HOURS_FOR_WEATHER_CALCULATION)
    averageTemperature = openWeatherHandler.getAverageTemperature(8)

    wateringDuration = appSettings["Watering"]["WateringDurationInSeconds"]
    delayBetweenWatering = appSettings["Watering"]["DelayBetweenWateringInSeconds"]

    # RULESET
    if averageProbabilityOfRain <= 20:
        if (averageTemperature > 16):
            logging.info("Repeat watering with intesity of %s  watering duration %s and delay %s." % (WATERING_INTENSITY_LEVEL_HIGH, wateringDuration, delayBetweenWatering))
            smartPlugHandler.repeat(WATERING_INTENSITY_LEVEL_HIGH, wateringDuration, delayBetweenWatering)
        else:
            logging.info("Repeat watering with intesity of %s  watering duration %s and delay %s." % (WATERING_INTENSITY_LEVEL_MEDIUM, wateringDuration, delayBetweenWatering))
            smartPlugHandler.repeat(WATERING_INTENSITY_LEVEL_MEDIUM, wateringDuration, delayBetweenWatering)
        return
    
    if 20 < averageProbabilityOfRain <= 60:
        if (averageTemperature > 27):
            logging.info("Repeat watering with intesity of %s  watering duration %s and delay %s." % (WATERING_INTENSITY_LEVEL_HIGH, wateringDuration, delayBetweenWatering))
            smartPlugHandler.repeat(WATERING_INTENSITY_LEVEL_HIGH, wateringDuration, delayBetweenWatering)
        elif averageTemperature < 18:
            logging.info("Repeat watering with intesity of %s  watering duration %s and delay %s." % (WATERING_INTENSITY_LEVEL_LOW, wateringDuration, delayBetweenWatering))
            smartPlugHandler.repeat(WATERING_INTENSITY_LEVEL_LOW, wateringDuration, delayBetweenWatering)
        else:
            logging.info("Repeat watering with intesity of %s  watering duration %s and delay %s." % (WATERING_INTENSITY_LEVEL_MEDIUM, wateringDuration, delayBetweenWatering))
            smartPlugHandler.repeat(WATERING_INTENSITY_LEVEL_MEDIUM, wateringDuration, delayBetweenWatering)
        return
    
    if averageProbabilityOfRain > 60:
        if averageTemperature > 27:
            logging.info("Repeat watering with intesity of %s  watering duration %s and delay %s." % (WATERING_INTENSITY_LEVEL_MEDIUM, wateringDuration, delayBetweenWatering))
            smartPlugHandler.repeat(WATERING_INTENSITY_LEVEL_MEDIUM, wateringDuration, delayBetweenWatering)
        else:
            logging.info("Repeat watering with intesity of %s  watering duration %s and delay %s." % (WATERING_INTENSITY_LEVEL_LOW, wateringDuration, delayBetweenWatering))
            smartPlugHandler.repeat(WATERING_INTENSITY_LEVEL_LOW, wateringDuration, delayBetweenWatering)
        return

if __name__ == '__main__':
    initSettings()
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        initLogging()

        initWeatherHandler()
        initSmartPlugHandler()

        schedulerThread = threading.Thread(target=startScheduler)  
        schedulerThread.start()
    port = appSettings["AppSettings"]["Port"]
    app.run(host="localhost", port=port, debug=True) #, use_reloader=False)
        