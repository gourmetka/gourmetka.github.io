#!/usr/bin/python3

# requies: simplejson, geopy, qwikidata

import urllib.request
import simplejson as json
import os
from datetime import datetime
import geopy.geocoders
from geopy.geocoders import Nominatim
import qwikidata
import qwikidata.sparql
import re
import time

geopy.geocoders.options.default_user_agent = 'covid-19'
geopy.geocoders.options.default_timeout = 7
geolocator = Nominatim()

# https://stackoverflow.com/questions/42335273/python-getting-the-population-of-a-city-given-its-name
def get_city_wikidata(city, country):
  time.sleep(1)
  query = """
  SELECT ?city ?cityLabel ?country ?countryLabel ?population
  WHERE
  {
    ?city rdfs:label '%s'@de.
    ?city wdt:P1082 ?population.
    ?city wdt:P17 ?country.
    ?city rdfs:label ?cityLabel.
    ?country rdfs:label ?countryLabel.
    FILTER(LANG(?cityLabel) = "de").
    FILTER(LANG(?countryLabel) = "de").
    FILTER(CONTAINS(?countryLabel, "%s")).
  }
  """ % (city, country)
  try:
    res = qwikidata.sparql.return_sparql_query_results(query)
    if len(res['results']['bindings']) > 0:
      out = res['results']['bindings'][0]
      return out
  except:
    print ("[ERR] Error when parsing res: %s" % city)
  return None

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

missing_population_map = {
    "Enzkreis": 198905,
    "Schwarzwald-Baar-Kreis": 212381,
    "Neustadt an der Aisch-Bad Windsheim": 100364,
    "Dahme-Spreewald": 169067,
    "Elbe-Elster": 102638,
    "Märkisch-Oderland": 194328,
    "Oberhavel": 211249,
    "Oberspreewald-Lausitz": 110476,
    "Oder-Spree": 178658,
    "Potsdam-Mittelmark": 214664,
    "Spree-Neiße": 114429,
    "Teltow-Fläming": 168296,
    "Hochtaunuskreis": 236564,
    "Rheingau-Taunus-Kreis": 187157,
    "Vogelsbergkreis": 	105878,
    "Wetteraukreis": 306460,
    "Vorpommern-Greifswald": 236697,
    "Vorpommern-Rügen": 224684,
    "Hameln-Pyrmont": 148559,
    "Heidekreis": 139755,
    "Lippe": 348391,
    "Rhein-Erft-Kreis": 470089,
    "Rhein-Kreis Neuss": 451007,
    "Rhein-Sieg-Kreis": 599780,
    "Frankenthal (Pfalz)": 48561,
    "Rhein-Hunsrück-Kreis": 102937,
    "Rhein-Lahn-Kreis": 122308,
    "Rhein-Pfalz-Kreis": 154201,
    "Westerwaldkreis": 201597,
    "Regionalverband Saarbrücken": 329708,
    "Erzgebirgskreis": 337696,
    "Burgenlandkreis": 180190,
    "Jerichower Land": 89928,
    "Salzlandkreis": 190560,
    "Ostholstein": 200581,
    "Schleswig-Flensburg": 200025,
    "Münster": 314319,
    "Bergstraße": 268780,
    "Grafschaft Bentheim": 135770,
    "Vulkaneifel": 60757,
    "Dithmarschen": 133560,
    "Nordfriesland": 164926,
    "Barnim": 180864,
    "Havelland": 160710,
    "Mecklenburgische Seenplatte": 261816,
    "Helmstedt": 91720,
    "Holzminden": 19998,
    "Ludwigslust-Parchim": 212618,
    "Mittelsachsen": 306185,
    "Vogtlandkreis": 227796,
    "Aichach-Friedberg": 133596,
    "Unterallgäu": 144041,
    "Wunsiedel im Fichtelgebirge": 9259,
    "Limburg-Weilburg": 172083,
    "Werra-Meißner-Kreis": 101017,
    "Nordwestmecklenburg": 156729,
    "Berchtesgadener Land": 24420,
    "Freyung-Grafenau": 78355,
    "Südwestpfalz": 95113,
    "Tier-Saarburg": 147833
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

    if "var legend" in d.decode("utf-8") and loader_state == True:
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
  # print ("Getting state info of: %s" % city)
  if city in city_name_obj.keys():
    return city_name_obj[city]
  else:
    location = locationofGeo(city, lat, long)
  return location.raw['address']['state']

def getPopupation(city_population_obj, city):
  # print ("Get population of: %s" % city)
  city = city.replace("(city and county)", "").strip()
  if city in city_population_obj.keys():
    # print ("[EXIST] found data for %s" % city)
    return city_population_obj[city]
  elif city in missing_population_map.keys():
    return missing_population_map[city]
  else:
    wiki_obj = get_city_wikidata(city, "Deutschland")
    if wiki_obj is not None:
      return int(wiki_obj["population"]["value"])
    else:
      # print ("[ERR] Wikidata doesn't have population data for %s" % city)
      print (city)
      return -1

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
city_data_exists_population = {}

for d in existing_city_data:
  if d["state"].strip() != "":
    city_data_exists_state[d["city_name"]] = d["state"].strip()
  if "population" in d.keys() and d["population"] != -1 and d["population"] != -2:
    city_data_exists_population[d["city_name"].replace("(city and county)", "").strip()] = d["population"]

city_objects = []
for city in city_list:
  city_object = {
    "city_name": city[2],
    "infected": int(city[3]),
    "geo": [city[0], city[1]],
    "state": stateofCity(region_city_map, city[2], city[0], city[1]),
    "population": getPopupation(city_data_exists_population, city[2])
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