#!/usr/bin/env python3

import cgitb
import cx_Oracle
cgitb.enable(format='text')
from jinja2 import Environment, FileSystemLoader
import folium
import pandas as pd
import os
import json

edinburgh_coords = [55.948795,-3.200226]

def render_html():
    env = Environment(loader=FileSystemLoader('.'))
    temp = env.get_template('index.html')
    inpFol = foliumMap()
    print(temp.render(map=inpFol))


def foliumMap():
    map1 = folium.Map(location = edinburgh_coords, zoom_start = 14)
    #conn = cx_Oracle.connect("student/train@geoslearn")
    with open('../../../details.txt', 'r') as f:
        pwd = f.readline().strip()
    conn = cx_Oracle.connect(f"s0092179/{pwd}@geoslearn")
    c = conn.cursor()

    c.execute("SELECT ogr_fid as id, naturalcom as name, sdo_util.to_geojson(ora_geometry) as wktgeometry FROM hoods")
    #geom = pd.DataFrame(columns=['id','name','geom'])
    for row in c:
        j = row[2]
        print(j)
        item = json.load(j)
        folium.GeoJson(item, name=row[1]).add_to(map1)
        #geom.loc[i] = row[0], row[1], j

    conn.close()

    return map1.get_root().render()


if __name__ == '__main__':
    print("Content-type: text/html\n")      #  Ensures that the webpage is rendered correctly using HTML code
    render_html()
