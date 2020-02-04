#!/usr/bin/env python3

import cgitb
import cx_Oracle
from jinja2 import Environment, FileSystemLoader
import folium
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.wkb import loads
import os
import json
cgitb.enable(format='text')

edinburgh_coords = [55.948795,-3.200226]

def render_html():
    env = Environment(loader=FileSystemLoader('.'))
    temp = env.get_template('index.html')
    inpFol = foliumMap()
    print(temp.render(map=inpFol))

class Hood():

    def __init__(self, id, name, geometry, srid='EPSG:27700'):
        self.id = id
        self.name = name
        self.geometry = geometry
        self.srid = srid

def foliumMap():
    map1 = folium.Map(location = edinburgh_coords, zoom_start = 14)
    #conn = cx_Oracle.connect("student/train@geoslearn")
    with open('../../../../details.txt', 'r') as f:
        pwd = f.readline().strip()
    conn = cx_Oracle.connect(f"s0092179/{pwd}@geoslearn")
    c = conn.cursor()


    c.execute("SELECT ogr_fid as id, naturalcom as name, sdo_util.to_wktgeometry(ora_geometry) as wktgeometry FROM hoods")

    geom = pd.DataFrame(columns=['id','name','geom'])
    i = 1
    areas_list = []
    for row in c:
        clean_coords = row[2].read()[16:-3]
        coords = [coord for coord in clean_coords.split(', ')]
        x = [x.split(' ')[0] for x in coords]
        y = [y.split(' ')[1] for y in coords]
        geom.loc[i] = row[0], row[1], np.array((x,y))
        name = f"area{str(i)}"
        name = Hood(row[0], row[1], geom)
        areas_list.append(name)
        i += 1

    print(geom)

    #for area in areas_list:
        #print(area.id, area.name, area.geometry)


    #gdf = gpd.GeoDataFrame(c.fetchall(), columns=['name', 'wktgeometry'])
    #gdf['geometry'] = gpd.GeoSeries(gdf['wktgeometry'].apply(lambda x: loads(x))
    #del gdf['wktgeometry']
    #print(gdf)

    # create GeoSeries to replace the WKB geometry column
    #gdf['geometry'] = gpd.GeoSeries(gdf['wkbgeometry'].apply(lambda x: loads(x)))
    #del gdf['wkbgeometry']

    # perform a basic GeoPandas operation (unary_union)
    # to combine the 3 adjacent states into 1 geometry
    #print()
    #print("GeoPandas combining the 3 geometries into a single geometry...")
    #print(gdf.unary_union)


    conn.close()

    return map1.get_root().render()


if __name__ == '__main__':
    print("Content-type: text/html\n")      #  Ensures that the webpage is rendered correctly using HTML code
    #render_html()
    map1 = foliumMap()
