#!/usr/bin/env python3
import cgi
import cx_Oracle

form = cgi.FieldStorage()

def Filter():
    zone_choice = form.getvalue("parking") # controlled, priority, parking
    filter_choice = form.getvalue("park-filter") # outside, inside, distance
    cont = ''
    chp = 1
    filter = ''


    if filter_choice == 'outside':
        cont = ' NOT '
    elif filter_choice == 'inside':
        cont = cont
    filter = "A.NAME "+str(cont)+"IN (SELECT A.NAME FROM s0092179.PARKING_8307 P, \
    CINEMAS A WHERE P.\"Type\"='"+str(zone_choice)+"' AND \
    SDO_GEOM.RELATE(A.GEOM, \
        'anyinteract', P.ORA_GEOMETRY, 0.5) = 'TRUE') "

    if filter_choice == 'distance':
        dist_choice = form.getvalue("park-dist")
        filter = "A.NAME IN (SELECT A.NAME FROM CINEMAS A, s0092179.PARKING_8307 P \
        WHERE P.\"Type\"='"+str(zone_choice)+"' AND \
        SDO_GEOM.RELATE((SDO_GEOM.SDO_BUFFER(A.GEOM,"+str(dist_choice)+",0.5)), 'ANYINTERACT', \
        P.ORA_GEOMETRY) = 'TRUE') "

    if zone_choice == None or filter_choice == None:
        chp = 0
        filter = ''

    return filter, chp
