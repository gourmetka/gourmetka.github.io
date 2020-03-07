#!/usr/local/bin/python3

import urllib.request
import simplejson as json
import os
from datetime import datetime

script_dir = os.path.dirname(__file__)

diff_name_region_map = {
  "Bavaria": "Bayern",
  "Hesse": "Hessen",
  "Mecklenburg-Western Pomerania": "Mecklenburg-Vorpommern",
  "Lower Saxony": "Niedersachsen",
  "North Rhine-Westphalia": "Nordrhein-Westfalen",
  "Rhineland-Palatinate": "Rheinland-Pfalz",
  "Saxony": "Sachsen",
  "Thuringia": "Thüringen"
}

url = "https://www.gcber.org/corona/"
user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"
headers = { 'User-Agent' : user_agent }

req = urllib.request.Request(url=url, headers=headers)
web = urllib.request.urlopen(req)
print ("code: %d" % web.getcode())
data = web.readlines()

region_list = []
for d in data:
  if "Bavaria" in d.decode("utf-8"):
    source = d.decode("utf-8")
    source = source.strip()[:-1].replace("'", '"')
    source = "[%s]" % source
    source_obj = json.loads(source)
    region_list = source_obj
    break

city_list = []
for d in data:
  if "Biberach" in d.decode("utf-8"):
    source = d.decode("utf-8")
    source = source.strip()[:-1].replace("'", '"')
    source = "[%s]" % source
    source_obj = json.loads(source)
    city_list = source_obj
    break

city_objects = []
for city in city_list:
  city_object = {
    "city_name": city[2],
    "infected": int(city[3]),
    "geo": [city[0], city[1]],
    "state": ""
  }
  city_objects.append(city_object)

existing_data = {}
with open(os.path.join(script_dir, '../data.json')) as f:
  existing_data = json.load(f)

for region in region_list:
  region_name = region[2]
  number_text = region[3].replace("confirmed cases", "").replace("confirmed case", "").strip()
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

output = json.dumps(existing_data, indent=2)
with open(os.path.join(script_dir, '../data.json'), 'w', encoding="utf-8") as f:
  f.write(output)
  f.close()

output = json.dumps(city_objects, indent=2)
with open(os.path.join(script_dir, '../city_data.json'), 'w+', encoding="utf-8") as f:
  f.write(output)
  f.close()

print ("done")
