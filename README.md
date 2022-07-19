# DeliveryAPI
![image](https://user-images.githubusercontent.com/57361655/179813624-3e7b0a23-bc3a-4b8e-96e9-075debef8ef3.png)

A simple delivery server with FastAPI.

## Requirments:
``
pip install -r /path/to/requirements.txt
``

## How to run:
``
uvicorn main:app 
``

Also need a file `constants.py` in the main project path to set the values of:

``DB_URL = `` => The path to the DB.

``HOLIDAY_API_KEY = `` => `https://holidayapi.com/docs` API key.

``GEO_API_KEY = `` => `https://www.geoapify.com/geocoding-api` API key.

(Could be replaced with env vars)

## How does it work?

### Setup and update:
Will start in a sperated thread - the setup will load `courier_API.json` when starting the server, that would add timeslots and adresses to the DB.
After that, a scheduler that will run every week to load the next weeks timeslots from `courier_API.json`.

### Web server:
A REST API for deliveries - can get addresses, timeslots, book a delivery, update a delivery and more.
