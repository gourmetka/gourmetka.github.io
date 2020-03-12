#!/usr/bin/python3

# requies: simplejson, geopy

import urllib.request
import simplejson as json
import os
from datetime import datetime
import geopy.geocoders
from geopy.geocoders import Nominatim
import re

geopy.geocoders.options.default_user_agent = 'covid-19'
geopy.geocoders.options.default_timeout = 7
geolocator = Nominatim()

script_dir = os.path.dirname(__file__)

diff_name_region_map = {
  "Bavaria": "Bayern",
  "Hesse": "Hessen",
  "Mecklenburg-Western Pomerania": "Mecklenburg-Vorpommern",
  "Lower Saxony": "Niedersachsen",
  "North Rhine-Westphalia": "Nordrhein-Westfalen",
  "Rhineland-Palatinate": "Rheinland-Pfalz",
  "Saxony": "Sachsen",
  "Saxony-Anhalt": "Sachsen-Anhalt",
  "Thuringia": "Thüringen"
}

def loader(data, keyword):
  loader_state = False
  region_array_str = ""
  for d in data:
    if keyword in d.decode("utf-8"):
      loader_state = True
      continue

    if loader_state == True:
      source = d.decode("utf-8")
      region_array_str += source.strip()
    
    if "];" in d.decode("utf-8") and loader_state == True:
      loader_state = False
      break
  source = "[%s]" % region_array_str.replace("'", '"').replace("];", "")[:-1]
  return json.loads(source)

def get_state_city_map(data):
  loader_state = False
  state_city_map = {}
  current_state = ""
  for d in data:
    if "var entryTable" in d.decode("utf-8"):
      loader_state = True
      continue

    if ";" in d.decode("utf-8") and loader_state == True:
      loader_state = False
      break

    if loader_state == True:
      source = d.decode("utf-8")
      if 'class="head"' in source:
        raw_state_name = re.sub("<(.*?)>", "", source.strip()).replace("'" ,"").strip()[1:]
        current_state = diff_name_region_map[raw_state_name] if raw_state_name in diff_name_region_map else raw_state_name
      else:
        city_name = re.sub("<(.*?)>", "", source.split("</td><td>")[0]).replace("'" ,"").strip()[1:]
        state_city_map[city_name] = current_state
  return state_city_map


def stateofCity(city_name_obj, city, lat, long):
  print ("Getting state info of: %s" % city)
  if city in city_name_obj.keys():
    return city_name_obj[city]
  else:
    location = locationofGeo(city, lat, long)
  return location.raw['address']['state']

def locationofGeo(city,lat,long):
  geoPoint = geopy.point.Point(lat, long)
  location = geolocator.reverse(geoPoint)
  if location.raw['address'].get('state') == None:
    location = geolocator.geocode(city,addressdetails=True)
  return location

url = "https://www.gcber.org/corona/"
user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"
headers = { 'User-Agent' : user_agent }

req = urllib.request.Request(url=url, headers=headers)
web = urllib.request.urlopen(req)
print ("code: %d" % web.getcode())
data = web.readlines()

region_list = loader(data, "var regionList")
city_list = loader(data, "var entryList")
region_city_map = get_state_city_map(data)

germany_recoveries = 0
germany_deaths = 0

for d in data:
  if "L.marker" in d.decode("utf-8") and "Germany" in d.decode("utf-8"):
    source = d.decode("utf-8")
    germany_status = source.split("+")[3].replace('"', '').split("|")
    germany_recoveries = int(germany_status[0].replace("recoveries", "").strip())
    germany_deaths = int(germany_status[1].replace("deaths", "").strip())
    break

existing_city_data = []
if os.path.exists(os.path.join(script_dir, '../city_data.json')):
  with open(os.path.join(script_dir, '../city_data.json')) as f:
    existing_city_data = json.load(f)

city_data_exists_state = {}

for d in existing_city_data:
  if d["state"].strip() != "":
    city_data_exists_state[d["city_name"]] = d["state"].strip()

city_objects = []
for city in city_list:
  city_object = {
    "city_name": city[2],
    "infected": int(city[3]),
    "geo": [city[0], city[1]],
    "state": stateofCity(region_city_map, city[2], city[0], city[1])
  }
  city_objects.append(city_object)

existing_data = {}
with open(os.path.join(script_dir, '../data.json')) as f:
  existing_data = json.load(f)

for region in region_list:
  region_name = region[2]
  number_text = region[3].replace("confirmed cases", "").replace("confirmed case", "").replace("&thinsp;", "").strip()
  number_cases = int(number_text)
  data = existing_data["data"]
  found = False
  for d in data:
    if region_name == d["stateName"]:
      d["infected"] = number_cases
      found = True
      break
    else:
      if region_name in diff_name_region_map.keys():
        mapped_region_name = diff_name_region_map[region_name]
        if mapped_region_name == d["stateName"]:
          d["infected"] = number_cases
          found = True
          break
  if found == False:
    print (region_name)

ts = int(datetime.now().timestamp()) * 1000
existing_data["ts"] = ts
existing_data["recoveries"] = germany_recoveries
existing_data["deaths"] = germany_deaths

output = json.dumps(existing_data, indent=2)
with open(os.path.join(script_dir, '../data.json'), 'w', encoding="utf-8") as f:
  f.write(output)
  f.close()

output = json.dumps(city_objects, indent=2)
with open(os.path.join(script_dir, '../city_data.json'), 'w+', encoding="utf-8") as f:
  f.write(output)
  f.close()

print ("done")