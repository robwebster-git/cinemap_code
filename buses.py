#!/usr/bin/env python3
import cgi
import cx_Oracle

form = cgi.FieldStorage()

def Filter():
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

    if stop_chp == 1 and route_chp == 1:
        stop_filter = "B_S.STOP = '"+str(stop_choice)+"' AND "
        filter = "A.NAME IN (SELECT A.NAME FROM s1434165.CINEMAS A,\
         s1983906.BUS_STOPS B_S WHERE "+str(stop_filter)+"\
         SDO_GEOM.WITHIN_DISTANCE(A.GEOM, "+str(bus_dist)+",\
          B_S.GEOM, 5, 'unit=METER') = 'TRUE') "
    if stop_chp == 0 and route_chp == 1:
        filter = "A.NAME IN (SELECT A.NAME FROM s1434165.CINEMAS A WHERE\
         SDO_GEOM.RELATE(A.GEOM, 'ANYINTERACT',\
          (SELECT SDO_GEOM.SDO_BUFFER(B.ORA_GEOMETRY,\
           "+str(bus_dist)+", 5) FROM s0092179.BUSROUTES_8307 B\
            WHERE B.OGR_FID ="+str(route_choice)+"), 0.5) = 'TRUE') "

    return filter, route_chp
