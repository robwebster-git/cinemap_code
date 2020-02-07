#!/usr/bin/env python3

import cgitb
import cx_Oracle
cgitb.enable(format='text')
import cgi
from jinja2 import Environment, FileSystemLoader
import folium
import pandas as pd
import os
import json
from pyproj import Proj, transform
import gdal

form = cgi.FieldStorage()

edinburgh_coords = [55.948795,-3.200226]

project_3857 = Proj(init="epsg:3857")
project_4326 = Proj(init="epsg:4326")
project_27700 = Proj(init="epsg:27700")


def render_html():
    env = Environment(loader=FileSystemLoader('.'))
    temp = env.get_template('index.html')
    inpFol = foliumMap()
    print(temp.render(map=inpFol))


def foliumMap():
    map1 = folium.Map(location = edinburgh_coords, zoom_start = 13)
    overlays1 = folium.FeatureGroup(name='Areas of Edinburgh')
    overlays2 = folium.FeatureGroup(name='Bus Routes')
    with open('../../../details.txt', 'r') as f:
        pwd = f.readline().strip()
    conn = cx_Oracle.connect(f"s0092179/{pwd}@geoslearn")
    c = conn.cursor()

    c.execute("SELECT ogr_fid as id, naturalcom as name, sdo_util.to_geojson(ora_geometry) as jsongeometry FROM hoods_4326")
    #geom = pd.DataFrame(columns=['id','name','geom'])
    ids = []
    names = []
    jsons_4326 = []

    for row in c:
        ids.append(row[0])
        names.append(row[1])
        item = json.load(row[2])
        jsons_4326.append(item)
        area_id = f"area{row[0]}"
        area_name = row[1]
        folium.GeoJson(item, name=area_id).add_to(overlays1)
        #print(f"({area_id}, {area_name})")


    c.execute("SELECT OGR_FID, sdo_util.to_geojson(ora_geometry) as jsongeometry from busroutes_4326")
    for row in c:
        name = row[0]
        data = json.load(row[1])
        print(data)
        folium.GeoJson(data, name=name).add_to(overlays2)
        #print(f"name: {name}, data:{data}")


    conn.close()

    overlays1.add_to(map1)
    overlays2.add_to(map1)
    folium.LayerControl().add_to(map1)



    return map1.get_root().render()


if __name__ == '__main__':
    print("Content-type: text/html\n")      #  Ensures that the webpage is rendered correctly using HTML code
    render_html()
