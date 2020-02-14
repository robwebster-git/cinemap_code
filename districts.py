#!/usr/bin/env python3
import cgi
import cx_Oracle

form = cgi.FieldStorage()

def Filter():
    dist_filter = form.getvalue("district-filter")
    dist_choice = form.getvalue("district-name")

    cont = ''
    filter = ''
    chp = 1

    if dist_filter == 'not-in':
        cont = ' NOT '
    if dist_filter == 'in':
        cont = cont
    filter = "A.NAME "+str(cont)+"IN (SELECT A.NAME FROM s1434165.CINEMAS A, s0092179.HOODS_8307 P \
    WHERE P.NATURALCOM='"+str(dist_choice)+"' AND \
    SDO_GEOM.RELATE(A.GEOM, \
        'anyinteract', P.ORA_GEOMETRY, 0.5) = 'TRUE') "

    if dist_filter == 'adj':
        filter = "A.NAME IN (SELECT A.NAME FROM s1434165.CINEMAS A WHERE SDO_GEOM.RELATE(A.GEOM, 'ANYINTERACT',(\
        SELECT SDO_AGGR_UNION(SDOAGGRTYPE(A.ORA_GEOMETRY,0.05))\
        FROM s0092179.HOODS_8307 A\
        WHERE SDO_GEOM.RELATE(\
          A.ORA_GEOMETRY, 'ANYINTERACT',\
          (SELECT A.ORA_GEOMETRY FROM s0092179.HOODS_8307 A\
            WHERE A.NATURALCOM = '"+str(dist_choice)+"'), 0.5) = 'TRUE'), 0.5) = 'TRUE') "

    if dist_filter == None:
        filter = ''
        chp = 0

    return filter, chp
