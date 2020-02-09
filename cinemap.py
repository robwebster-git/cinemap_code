#!/usr/bin/env python3
"""
s0092179.HOODS_4326 H
s0092179.PARKING P
s0092179.SECTORS SEC
s0092179.BUSROUTES_4326
s1983906.BUS_STOPS B_S
"""
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
    film, chp2 = filmFilter()
    rest, chp3 = restDistFilter()
    bus, chp4 = busFilter()

    var1 = ''
    var2 = ''
    var3 = ''

    # if something has been selected as a filter
    if 1 in (chp1,chp2,chp3,chp4):
        where = 'WHERE ' # start a where statement
    else:
        where = '' # otherwise don't

    # if two filters have been selected, join them
    if chp1 == 1 and any([chp2 == 1, chp3 ==1, chp4 == 1]):
        var1 = ' AND '

    if chp2 == 1 and chp3 == 1:
        var2 = ' AND '

    if chp3 and chp4 == 1:
        var3 = ' AND '


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
    filter = where + facilities + var1 + film + var2 + rest + var3 + bus + group

    map1 = folium.Map(location = edinburgh_coords, zoom_start = 13)

    conn = cx_Oracle.connect(user=user, password=pwd, dsn="geoslearn")
    c = conn.cursor()
    c.execute(sql+filter)
    for row in c:
        folium.Marker(row[1:],popup=row[0],icon=folium.Icon(color='red', icon='film')).add_to(map1)


    c.execute("SELECT B.STOP, B.GEOM.SDO_POINT.Y, B.GEOM.SDO_POINT.X FROM s1983906.BUS_STOPS B")
    for row in c:
        folium.Marker(row[1:],popup=row[0],icon=folium.Icon(color='green', icon='road')).add_to(map1)


    print('<h6>Query: '+str(sql+filter)+'</h6>')
    conn.close()

    return map1.get_root().render()

def restFilter():
    choice = form.getvalue("rest")
    chp = 1
    filter = ''
    test_char = ''
    real_chars = ''

    rest_dict = {
    't': 'R.TYPE = ',
    'n': 'R.NAME = '
    }

    if choice in (None,'all'):
        chp = 0 # no choice
    else: # else search for it
        test_char = choice[0]
        real_chars = choice[1:]
        for j in rest_dict.keys():
            if test_char == j: # select corresponding column
                filter = rest_dict[j] + "'"+str(real_chars)+"' AND "

    return filter, chp

def restDistFilter():
    rest_choice, ignore = restFilter()
    dist_choice = form.getvalue("rest-dist")
    sub_filter = ""
    chp = 1

    if dist_choice in (None, '0'):
        sub_filter = sub_filter
        chp = 0
    else:
        sub_filter = "A.NAME IN (SELECT A.NAME FROM CINEMAS A, s1987402.RESTAURANTS R WHERE "+str(rest_choice)+"SDO_GEOM.WITHIN_DISTANCE(A.GEOM, "+str(dist_choice)+", R.GEOM, 5, 'unit=METER') = 'TRUE') "

    return sub_filter, chp

def busFilter():
    route_chp = 1
    stop_chp = 1
    filter = ''
    column = ''
    stop_filter = ''

    route_choice = form.getvalue("route")
    stop_choice = form.getvalue("stop")
    bus_dist = form.getvalue("bus-dist")

    if route_choice == None:
        route_chp = 0

    if stop_choice in (None,'any'):
        stop_chp = 0
        #query with buffer around bus route line

    if stop_chp == 1:
        stop_filter = "B_S.STOP = '"+str(stop_choice)+"' AND "
        filter = "A.NAME IN (SELECT A.NAME FROM CINEMAS A, s1983906.BUS_STOPS B_S WHERE "+str(stop_filter)+"SDO_GEOM.WITHIN_DISTANCE(A.GEOM, "+str(bus_dist)+", B_S.GEOM, 5, 'unit=METER') = 'TRUE') "

    return filter, route_chp

def filmFilter():
    """ Taking the user's choice of film and searching for it """
    filter = ''
    column = ''
    real_chars = ''
    choice = form.getvalue("film")
    chp = 1 # flag to indicate if choice has been made

    film_dict = {
    't': 'B.TITLE = ',
    'g': 'B.GENRE = ',
    'a': 'B.AGE_RATING = '
    }

    if choice in (None,'all'):
        chp = 0 # no choice
    else: # else search for it
        test_char = choice[0]
        real_chars = choice[1:]
        for j in film_dict.keys():
            if test_char == j: # select corresponding column
                filter = film_dict[j] + "'"+str(real_chars)+"' "



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
        filter = filter + str(i) + "='y' " + var

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
