#!/usr/bin/env python3
import cgi
import cx_Oracle

form = cgi.FieldStorage()

def Filter():
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
