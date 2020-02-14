#!/usr/bin/env python3
import cgi
import cx_Oracle

form = cgi.FieldStorage()

def Filter():
    choice = form.getvalue("shop")
    chp = 1
    filter = ''
    test_char = ''
    real_chars = ''

    shop_dict = {
    'n': 'S.NAME = ',
    'c': 'S.CATEGORY = '
    }

    if choice in (None,'all'):
        chp = 0 # no choice
    else: # else search for it
        test_char = choice[0]
        real_chars = choice[1:]
        for j in shop_dict.keys():
            if test_char == j: # select corresponding column
                filter = shop_dict[j] + "'"+str(real_chars)+"' AND "

    return filter, chp

def DistFilter():
    rest_choice, ignore = Filter()
    dist_choice = form.getvalue("shop-dist")
    sub_filter = ""
    chp = 1

    if dist_choice in (None, '0'):
        sub_filter = sub_filter
        chp = 0
    else:
        sub_filter = "A.NAME IN (SELECT A.NAME FROM s1434165.CINEMAS A, \
        s1987402.SHOPS S WHERE "+str(rest_choice)+"\
        SDO_GEOM.WITHIN_DISTANCE(A.GEOM, "+str(dist_choice)+", \
        S.GEOM, 10, 'unit=METER') = 'TRUE') "

    return sub_filter, chp
