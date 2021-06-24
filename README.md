# App.SmartWateringSystem
Automated watering system used for the our balcony plants while in holidays.
A calculation of the weater for the next 8 hours controls the intensity of water. 
The intensity is controlled by turning on and off the pump.

For the moment: Watering intensity with the values 3, 2 and 1 (It must be adjusted with your watering tubes).

# Components
- Raspberry Pi
- TP-Link Kasa WLAN Smart KP105
- Gardena city gardening holidy watering (1265-20)
- A box with around 50-100l volume

# How to use
1. Create a `settings.json` based on `settings_example.json`
    1. Possible configurations

# Installation on Raspberry
1. copy smartwatering.service into `/etc/systemd/system/`
    1. sudo systemctl start smartwatering
    1. sudo systemctl enable smartwatering
1. copy nginx config to `/etc/nginx/sites-available/`
    1. sudo ln -s /etc/nginx/sites-available/nginx_smartwatering /etc/nginx/sites-enabled
    1. sudo nginx -t
    1. sudo systemctl restart nginx

# Future work
1. wsgi configuration
1. Buttons to handle PowerPlug via WebInterface
1. Show status on WebInterface
1. Adding css like Bootstrap
1. Better weather calculation
1. Better intensity control
1. Cleanup code