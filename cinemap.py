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

    c.execute("SELECT * FROM CINEMAS")
    for row in c:
        folium.Marker(row[2:4], popup=row[1], icon=folium.Icon(color='blue', icon='glyphicon-facetime-video')).add_to(map1)

    c.execute("SELECT * FROM RESTAURANTS")
    for row in c:
            folium.Marker(row[2:4], popup=row[1], icon=folium.Icon(color='red', icon='glyphicon-cutlery')).add_to(map1)

    c.execute("SELECT * FROM JSON_EXAMPLE")
    for row in c:
        thing = json.load(row[1])
        folium.GeoJson(thing, name='meadows').add_to(map1)

    conn.close()

    #  Circle marker example
    folium.CircleMarker(
        location=[55.948795,-3.200226],
        radius=50,
        popup='POPUP TEXT OF YOUR CHOICE',
        color='#428bca',
        fill=True,
        fill_color='#428bca'
    ).add_to(map1)

    #meadows = os.path.join('geojson','meadows.json')

    # GeoJSON example
    #folium.GeoJson(meadows, name='meadows').add_to(map1)

    return map1.get_root().render()



def getDBdata(table_name='CINEMAS', order_column='CINEMA_ID'):
    #  Accesses the Oracle database and creates Find, Field, Crop & MyClass
    #  objects with which to create the website visualiser tools
    results = []
    with open('../../../details.txt', 'r') as f:
        pwd = f.readline().strip()
    try:
        conn = cx_Oracle.connect(f"s0092179/{pwd}@geoslearn")
        c = conn.cursor()
        c.execute(f"SELECT * FROM {table_name} ORDER BY {order_column}")
    except:
        print("Failed to connect to Database Server...")

    if table_name == "CINEMAS":
        cinemas_list = []
        for row in c:
            (a, b, c, d, e) = row
            cinema_name = table_name[:-1] + str(a)
            cinema_name = Cinema(a, b, c, d, e)
            cinemas_list.append(cinema_name)
            results = cinemas_list
    else:                                             #  if no table name matches are made, go to the else...
        print("Table Name not supported...")
    conn.close()                                      #  close the connection to the Oracle server
    return results

if __name__ == '__main__':
    print("Content-type: text/html\n")      #  Ensures that the webpage is rendered correctly using HTML code
    render_html()
