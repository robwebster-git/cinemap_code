#!/usr/bin/env python3
import cgi
import cx_Oracle

form = cgi.FieldStorage()

def Choice():
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

def Filter():
    """ Taking user choice and integrating into SQL """

    # set up the SQL
    crit, chp = Choice()
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
