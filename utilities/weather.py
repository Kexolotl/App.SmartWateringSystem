import logging
import json
import requests
import statistics

class OpenWeatherHandler:
    _weatherData = []
    _appid = ""
    _latitude = ""
    _longitude = ""
    _unwantedWeatherData = []
    _wantedWeatherData = []
    _openWeatherUrl = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&units=metric&exclude=%s&appid=%s"

    def init(self, settings):
        self.appId = settings["AppId"]
        self._latitude = settings["Latitude"]
        self._longitude = settings["Langitude"]
        self._unwantedWeatherData = settings["UnwantedWeatherData"]
        self._wantedWeatherData = settings["WantedWeatherData"]
        logging.info("Initialize open weather handler with appId %s" % self.appId)

    def loadWeatherData(self):
        logging.info("Load weather data.")

        separator = ','
        unwantedWeatherDataAsString = separator.join(self._unwantedWeatherData)

        url = self._openWeatherUrl % (self._latitude, self._longitude, unwantedWeatherDataAsString, self.appId)
        try:
            response = requests.get(url)
            data = json.loads(response.text)
            self._weatherData = data
        except:
            self._weatherData = None

    def getAverageProbabilityOfRain(self):
        values = self._weatherData[self._wantedWeatherData[0]] # progrnose for daily
        today = values[0] # progrnose for daily
        if "rain" not in today:
            return 0
        else:
            return today["rain"]
    
    def getAverageProbabilityOfRainByHours(self, amountOfHours):
        values = self._weatherData[self._wantedWeatherData[0]] # progrnose for daily
        logging.info("Get average probability of rain for the next %s hours." % (amountOfHours))
        values = self._weatherData[self._wantedWeatherData[1]] # prognose for the next five days in hours
        rainPercentages = []
        for i in range(0, amountOfHours):
            valuesForHour = values[i]
            if ("rain" not in valuesForHour):
                continue
            rainPercentages.append(valuesForHour["rain"])

        if len(rainPercentages) == 0:
            return 0
        return statistics.mean(rainPercentages)

    def isRainingToday(self):
        logging.info("Get weather forcast for today")

        values = self._weatherData[self._wantedWeatherData[0]]
        today = values[0]
        return "Rain" in today["weather"][0]["main"]

    def getAverageTemperature(self, amountOfHours):
        logging.info("Get average temperature for the next %s hours." % (amountOfHours))

        values = self._weatherData[self._wantedWeatherData[1]] # prognose for the next five days in hours

        temperatures = []
        for i in range(0, amountOfHours):
            valuesForHour = values[i]
            temperatures.append(valuesForHour["temp"])
        return statistics.mean(temperatures)
