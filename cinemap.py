#!/usr/bin/env python3
"""
s0092179.HOODS_4326 H
s0092179.PARKING P
s0092179.SECTORS SEC
s0092179.BUSROUTES_4326
s1983906.BUS_STOPS B_S
"""


# External packages
import cgi
import cgitb
import cx_Oracle
cgitb.enable(format='text')
from jinja2 import Environment, FileSystemLoader
import folium

import os
import json


form = cgi.FieldStorage()

with open('/web/s1434165/public_html/cgi-bin/sensitive/pw.txt', 'r') as f:
    pwd = f.readline().strip()

def render_html():
    """ Function to render the page, putting the map inside the template """
    env = Environment(loader=FileSystemLoader('.'))
    temp = env.get_template('index.html')
    inpFol = foliumMap()
    print(temp.render(map=inpFol))

def foliumMap():
    """ Function to render the map with the query chosen """
    query = QueryBuilder()

    map1 = folium.Map(location = edinburgh_coords, zoom_start = 13)

    conn = cx_Oracle.connect(user=user, password=pwd, dsn="geoslearn")
    c = conn.cursor()
    c.execute(query)
    for row in c:
        folium.Marker(row[1:],popup=row[0],icon=folium.Icon(color='red', icon='film')).add_to(map1)

    print('<h6>Query: '+str(query)+'</h6>')
    conn.close()

    return map1.get_root().render()

def QueryBuilder():
    """ Function to build the SQL query based on user's choices or default """
    facilities, chp1 = fac.Filter()
    film, chp2 = films.Filter()
    rests, chp3 = rest.DistFilter()
    bus, chp4 = buses.Filter()
    shop, chp5 = shops.DistFilter()
    parks, chp6 = park.Filter()
    hood, chp7 = hoods.Filter()

    var1 = ''
    var2 = ''
    var3 = ''
    var4 = ''
    var5 = ''
    var6 = ''

    # if something has been selected as a filter
    if 1 in (chp1,chp2,chp3,chp4,chp5,chp6,chp7):
        where = 'WHERE ' # start a where statement
    else:
        where = '' # otherwise don't

    # if two filters have been selected, join them
    if chp1 == 1 and any([chp2 == 1, chp3 ==1, chp4 == 1, chp5 ==1, chp6==1, chp7==1]):
        var1 = ' AND '

    if chp2 == 1 and any([chp3 == 1, chp4 == 1, chp5 ==1, chp6==1, chp7==1]):
        var2 = ' AND '

    if chp3 and any([chp4 == 1, chp5 ==1, chp6==1, chp7==1]):
        var3 = ' AND '

    if chp4 and any([chp5 ==1, chp6==1, chp7==1]):
        var4 = ' AND '

    if chp5 and any([chp6==1, chp7==1]):
        var5 = ' AND '

    if chp6==1 and chp7==1:
        var6 = ' AND '

    # target data
    select = 'SELECT A.NAME, A.GEOM.SDO_POINT.Y, A.GEOM.SDO_POINT.X '
    # target table(s)
    tables = 'FROM CINEMAS A '
    # inner join for M2M table
    innerjoin = 'INNER JOIN CINEFILMRELATION AB ON A.CINEMA_ID = AB.CINEMA_ID INNER JOIN FILMS B ON B.FILM_ID = AB.FILM_ID '
    extjoins = 's1987402.RESTAURANTS R, s1987402.SHOPS S '
    # group results to avoid redundant repeats
    group = 'GROUP BY A.NAME, A.GEOM.SDO_POINT.Y, A.GEOM.SDO_POINT.X'

    sql = select + tables + innerjoin
    filters = where + facilities + var1 + film + var2 + rests + var3 + bus + var4 + shop + var5 + parks + var6 + hood + group

    query = sql + filters

    return query

if __name__ == '__main__':
    print("Content-type: text/html\n")      #  Ensures that the webpage is rendered correctly using HTML code
    render_html()
