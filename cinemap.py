#!/usr/bin/env python3

import cgi
import cgitb
import cx_Oracle
cgitb.enable(format='text')
from jinja2 import Environment, FileSystemLoader
import folium
import pandas as pd
import os
import json

edinburgh_coords = [55.948795,-3.200226]
user = "s1434165"
form = cgi.FieldStorage()

with open('/web/s1434165/public_html/cgi-bin/sensitive/pw.txt', 'r') as f:
    pwd = f.readline().strip()

def render_html():
    env = Environment(loader=FileSystemLoader('.'))
    temp = env.get_template('index.html')
    inpFol = foliumMap()
    print(temp.render(map=inpFol))

def foliumMap():
    facilities, chp1 = facilitiesFilter()
    film, chp2 = filmsFilter()
    var1 = ''

    # if something has been selected as a filter
    if 1 in (chp1,chp2):
        where = ' WHERE ' # start a where statement
    else:
        where = '' # otherwise don't

    # if two filters have been selected, join them
    if chp1 == 1 and chp2 == 1:
        var1 = ' AND '

    # target data
    select = 'SELECT A.NAME, A.GEOM.SDO_POINT.Y, A.GEOM.SDO_POINT.X '
    # target table(s)
    tables = 'FROM CINEMAS A '
    # inner join for M2M table
    joins = "INNER JOIN CINEFILMRELATION AB ON A.CINEMA_ID = AB.CINEMA_ID INNER JOIN FILMS B ON B.FILM_ID = AB.FILM_ID "

    sql = select + tables + joins
    filter = where + facilities + var1 + film

    map1 = folium.Map(location = edinburgh_coords, zoom_start = 14)

    conn = cx_Oracle.connect(user=user, password=pwd, dsn="geoslearn")
    c = conn.cursor()
    c.execute(sql+filter)

    for row in c:
        folium.Marker(row[1:],popup=row[0],icon=folium.Icon(color='red', icon='film')).add_to(map1)

    # printing query so we can watch whats going on
    print('<h6>Query: '+str(sql+filter)+'</h6>')
    conn.close()

    """
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
    """
    return map1.get_root().render()

def filmsFilter():
    """ Taking the user's choice of film and searching for it """
    filter = ''
    choice = form.getvalue("film")
    chp = 1 # flag to indicate if choice has been made

    if choice in (None,'all'):
        chp = 0 # no choice
    else: # else search for it
        filter = "B.TITLE = '" +str(choice)+"' "

    return filter, chp

def facilitiesChoice():
    """ Taking the user's choice(s) and selecting the relevant column """
    chp = 1
    fac_var = []
    choices = form.getlist("facilities")

    if isinstance(choices, list): # The user is requesting more than one item.
        fac_var = fac_var.append(choices)
    else:
        fac_var = choices
    # The user is requesting only one item.

    if len(choices)<1: # if user has selected nothing
        fac_var = [] # make blank
        chp = 0
    else:
        fac_var = choices # else take the choices

    crit = [] # empty list to fill with rows

    # dict relating user variables to relevant columns
    fac_filter_dict = {
    'bar': 'A.BAR',
    'popcorn': 'A.POPCORN',
    'access': 'A.WHEELCHAIR_ACC',
    'student': 'A.STUDENT_DISC'
    }

    # testing which user variable was selected
    for i in fac_var:
        for j in fac_filter_dict.keys():
            if i == j: # select corresponding column
                crit = crit + [fac_filter_dict[j]]

    # return column name(s) for use in the query
    return crit, chp

def facilitiesFilter():
    """ Taking user choice and integrating into SQL """

    # set up the SQL
    crit, chp = facilitiesChoice()
    filter = ''

    if chp == 0:
        filter = ''
    else:
        var = ' AND ' # to join the criteria(s)

    for i in crit:
        if i == crit[-1]: #if its the last criteria
            var = '' # no AND at the end
        filter = filter + str(i) + "='y'" + var

    # return completed query filter
    return filter, chp


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
