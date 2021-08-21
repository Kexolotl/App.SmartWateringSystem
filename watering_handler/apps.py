import os
import json
import logging

from datetime import datetime
from watering_handler.weather import OpenWeatherHandler
from watering_handler.smartplug import SmartPlugHandler
from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler

appSettings = None
smartPlugHandler = None
openWeatherHandler = None

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
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logLevel)
        logging.info('Configure local logging finisehd.')
        return

    if "LogFile" in appSettings["Logging"] and appSettings["Logging"]["LogFile"]:
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename=appSettings["Logging"]["LogFile"], level=logLevel)

    logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)
    logging.info('Configure logging finisehd.')

def initWeatherHandler():
    global openWeatherHandler
    openWeatherHandler = OpenWeatherHandler()
    openWeatherHandler.init(appSettings["OpenWeather"])
    logging.info('Configure weather handler finished.')

def initSmartPlugHandler():
    global smartPlugHandler
    smartPlugHandler = SmartPlugHandler(appSettings["SmartPlug"]["IpAddress"])
    logging.info('Configure smart plug handler finished.')
    #smartPlugHandler.connect()
    #smartPlugHandler.turnOff() # turn off initial

def emitWaterIntesity(averageProbabilityOfRain, averageTemperature):
    high_intensity = appSettings["WaterIntensityLevels"]["Watering_Intensity_Level_High"]
    medium_intensity = appSettings["WaterIntensityLevels"]["Watering_Intensity_Level_Medium"]
    low_intensity = appSettings["WaterIntensityLevels"]["Watering_Intensity_Level_Low"]
    none_intensity = appSettings["WaterIntensityLevels"]["Watering_Intensity_Level_None"]

    if (averageProbabilityOfRain > 30):
        return low_intensity

    if averageTemperature > 25:
        return high_intensity

    if averageTemperature <= 25 and averageTemperature > 18:
        return medium_intensity

    if averageTemperature < 18 and averageTemperature > 10:
        return low_intensity

    return none_intensity

def handleWatering():
    startAt = appSettings["Watering"]["TimeForWatering"]
    now = datetime.now()
    current_time = now.strftime("%H:%M")

    if not current_time == startAt:
        return

    do_watering()

def do_watering():
    try:
        openWeatherHandler.loadWeatherData()
            
        averageProbabilityOfRain = openWeatherHandler.getAverageProbabilityOfRain()
        averageTemperature = openWeatherHandler.getAverageTemperature(8)

        wateringDuration = appSettings["Watering"]["WateringDurationInSeconds"]
        delayBetweenWatering = appSettings["Watering"]["DelayBetweenWateringInSeconds"]

        logging.info("Average probability of rain: %s." % (averageProbabilityOfRain))
        logging.info("Average temperatur: %s." % (averageTemperature))

        waterIntensity = emitWaterIntesity(averageProbabilityOfRain, averageTemperature)
        logging.info("Repeat watering with intesity of %s  watering duration %s and delay %s." % (waterIntensity, wateringDuration, delayBetweenWatering))
        smartPlugHandler.repeat(waterIntensity, wateringDuration, delayBetweenWatering)
        
        # RAINING_DAY_BEFORE = openWeatherHandler.isRainingToday() # put to sqlite db        
    except Exception:
        logging.error("Error while handling watering.")
        return


class WateringHandlerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'watering_handler'

    def ready(self):
        # put your startup code here
        initSettings()
        initLogging()
        initWeatherHandler()
        initSmartPlugHandler()

        scheduler = BackgroundScheduler()
        scheduler.add_job(handleWatering, 'interval', minutes=1, id='my_job_id')
        scheduler.start()