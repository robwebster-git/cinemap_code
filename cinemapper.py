#!/web/s0092179/public_html/cgi-bin/cinemap/bin/python

import cgitb
import cx_Oracle
cgitb.enable(format='text')
import cgi
from jinja2 import Environment, FileSystemLoader
import folium
from folium import plugins
import os
import json
from branca.colormap import linear
import branca.colormap as cm
import random
from datetime import time

# Customised modules and functions
import parking as park
import restaurants as rest
import shops
import facilities as fac
import buses
import films
import districts as hoods


form = cgi.FieldStorage()
edinburgh_coords = [55.937495,-3.220226]

polycolours = linear.GnBu_06.scale(0,120)
polycolours.caption = 'Areas of Edinburgh'

colours = ['green', 'blue', 'red', 'orange', 'gray', 'yellow']

style1 = {'fillColor': 'red', 'color': 'red', 'weight': 2}
style3 = {'fillColor': 'blue', 'color': 'blue', 'weight': 2}

results_show = False
user_results_show = False

class Cinema:

    def __init__(self, id, name, lon, lat):

        self.id = id
        self.name = name
        self.lon = lon
        self.lat = lat
        self.films = []


def render_html():
    env = Environment(loader=FileSystemLoader('.'))
    temp = env.get_template('index_full.html')
    inpFol = foliumMap()
    print(temp.render(map=inpFol))

def user_location(c, lat, lon, distance, results, cinemas_list):
    c.execute(f"SELECT c.name, c.geom.sdo_point.y, c.geom.sdo_point.x from s1434165.cinemas c where SDO_GEOM.WITHIN_DISTANCE(c.geom, {distance}, SDO_GEOMETRY('POINT({lon} {lat})', 8307), 10, 'unit=METER') = 'TRUE'")
    folium.Circle(location=[lat, lon], radius=distance, tooltip=f"<h5>Cinemas within {distance} metres</h5>", color='#db910f', weight=5, fill=True).add_to(results)
    folium.Circle(location=[lat, lon], radius=50, color='#db910f', weight=5, fill=False).add_to(results)
    results.show = True
    for row in c:
        display = None
        name = row[0]
        try:
            if name == "Omni Centre":
                display = cinemas_list[2]
            elif name == "Dominion":
                display = cinemas_list[4]
            elif name == "Cameo":
                display = cinemas_list[5]
            elif name == "Filmhouse":
                display = cinemas_list[6]
            elif name == "Odeon Lothian":
                display = cinemas_list[3]
            elif name == "Cineworld":
                display = cinemas_list[0]
            elif name == "Scotsman Filmhouse":
                display = cinemas_list[1]
            else:
                continue
        except ValueError:
            print("No matching cinema...")

        html = folium.Html(display.popup_text, script=True)
        display.popup_html = folium.Popup(html, max_width=2650)
        folium.Marker(row[1:],popup=display.popup_html, tooltip=f"<h5>The {row[0]} cinema is less<br> than <emp>{int(int(distance)/70)}</emp> minutes walk away</h5>",icon=folium.Icon(color='orange', icon='glyphicon-screenshot')).add_to(results)
        #display.geoclose = True

    return c, results

def QueryBuilder(results):
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
        results.show=True
        results_show = True
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
    rest_select = ', r.name, r.geom.sdo_point.y, r.geom.sdo_point.x '
    shop_select = ', s.name, s.geom.sdo_point.y, s.geom.sdo_point.x '
    # target table(s)
    tables = 'FROM s1434165.CINEMAS A '
    rest_tables = ',s1987402.RESTAURANTS R '
    shop_tables = ',s1987402.SHOPS S '
    # inner join for M2M table
    innerjoin = 'INNER JOIN s1434165.CINEFILMRELATION AB ON A.CINEMA_ID = AB.CINEMA_ID INNER JOIN s1434165.FILMS B ON B.FILM_ID = AB.FILM_ID '
    extjoins = 's1987402.RESTAURANTS R, s1987402.SHOPS S '
    # group results to avoid redundant repeats
    group = 'GROUP BY A.NAME, A.GEOM.SDO_POINT.Y, A.GEOM.SDO_POINT.X'
    '''
    if chp3 == 1 and chp5 != 1:
        sql = select + rest_select + tables + rest_tables + innerjoin
    elif chp5 == 1 and chp3 == 1:
        sql = select + rest_select + shop_select + tables + rest_tables + shop_tables + innerjoin
    elif chp5 == 1 and chp3 != 1:
        sql = select + shop_select + tables + shop_tables + innerjoin
    else:
        sql = select + tables + innerjoin
    '''
    sql = select + tables + innerjoin
    filters = where + facilities + var1 + film + var2 + rests + var3 + bus + var4 + shop + var5 + parks + var6 + hood + group

    query = sql + filters

    return query, results, chp1, chp2, chp3, chp4, chp5, chp6, chp7


def foliumMap():
    """ Function to render the map with the query chosen """

    map1 = folium.Map(location = edinburgh_coords, tiles='openstreetmap', zoom_control=False, zoom_start = 14)

    folium.TileLayer('cartodbpositron', name="CartoDB Positron", attr='Carto DB').add_to(map1)
    folium.TileLayer('cartodbdark_matter', name="CartoDB DarkMatter", attr='Carto DB').add_to(map1)
    folium.TileLayer('stamentoner', name="Stamen Toner", attr='Stamen Toner').add_to(map1)

    plugins.LocateControl(auto_start=True, flyTo=False, returnToPrevBounds=True, enableHighAccuracy=False, position='topright').add_to(map1)
    plugins.Fullscreen(position='topright', title='Foolish screen', title_cancel='Return to normality', force_separate_button=True).add_to(map1)

    #minimap_layer = folium.FeatureGroup(name="Minimap")
    user_results_layer = folium.FeatureGroup(name="User Location Results", show=user_results_show)
    results_layer = folium.FeatureGroup(name="Results", show=results_show)
    area_layer = folium.FeatureGroup(name='Areas of Edinburgh', show=False)
    bus_layer = folium.FeatureGroup(name='Bus Routes', show=False)
    bus_stop_layer = folium.FeatureGroup(name='Bus Stops', show=False)
    cinema_layer = folium.FeatureGroup(name='Cinemas')
    shop_layer = folium.FeatureGroup(name='Shops', show=False)
    restaurant_layer = folium.FeatureGroup(name='Restaurants', show=False)
    parking_layer = folium.FeatureGroup(name='Parking Zones', show=False)


    #plugins.MiniMap().add_to(minimap_layer)

    with open('../../../details.txt', 'r') as f:
        pwd = f.readline().strip()
    conn = cx_Oracle.connect(f"s0092179/{pwd}@geoslearn")
    c = conn.cursor()

    query, results_layer, ch1, ch2, ch3, ch4, ch5, ch6, ch7 = QueryBuilder(results_layer)

    c.execute("SELECT a.ogr_fid, a.\"Type\", a.\"Zone_No\", sdo_util.to_geojson(a.ora_geometry) FROM parking_8307 a")
    for row in c:
        id = int(row[0])
        colour = 'yellow'
        zone_no = row[2]
        park_type = row[1]
        if park_type == "Free":
            colour = 'green'
        elif park_type == "Controlled parking zone":
            colour = 'red'
        else:
            colour = 'orange'
        item = json.load(row[3])
        zone = folium.Choropleth(geo_data=item, line_color='orange', line_opacity=1, legend_name='Parking Areas', fill_opacity=0.3, fill_color=colour).add_to(parking_layer)
        folium.Tooltip(text=f"Zone {zone_no} is : {park_type}", style=f"color:{colour}; font-weight:bold;", sticky=False).add_to(zone)

    c.execute("SELECT ogr_fid as id, naturalcom as name, sdo_util.to_geojson(ora_geometry) as jsongeometry FROM hoods_8307")
    jsons_4326 = []
    for row in c:
        id = int(row[0])
        colour = colours[(id%6)]
        style2 = {'fillColor': '#fc7303', 'color': colour, 'weight': 3}
        name = row[1]
        item = json.load(row[2])
        jsons_4326.append(item)
        area_id = f"area{row[0]}"
        area_name = row[1]
        name = folium.Choropleth(geo_data=item, tooltip=area_name, line_color='orange', line_opacity=1, legend_name='Edinburgh District', fill_opacity=0.6, fill_color=polycolours(id)).add_to(area_layer)
        folium.Tooltip(text=area_name, style="color:red;", sticky=False).add_to(name)


    c.execute("SELECT OGR_FID, sdo_util.to_geojson(ora_geometry) as jsongeometry from busroutes_8307")
    for row in c:
        name = row[0]
        data = json.load(row[1])
        if name == 1:
            one = folium.GeoJson(data, name=name, style_function = lambda x: style1).add_to(bus_layer)
            folium.Popup(html="<h3 style=\"min-width: 180px; color:red;\">Bus Route 1</h3><h4 style=\"color:red;\">Leith to Comiston</h4>").add_to(one)
        if name == 2:
            two = folium.GeoJson(data, name=name, style_function = lambda x: style3).add_to(bus_layer)
            folium.Popup(html="<h3 style=\"min-width: 180px; color:blue;\">Bus Route 2</h3><h4 style=\"color:blue;\">Stockbridge to Newington</h4>").add_to(two)

    c.execute("SELECT UNIQUE a.CINEMA_ID, a.NAME, b.title, c.time1, c.time2, c.time3, a.GEOM.sdo_point.x as lon, a.GEOM.sdo_point.y as lat from s1434165.cinemas a, s1434165.films b, s1434165.cinefilmrelation c where c.film_id = b.film_id and c.cinema_id = a.cinema_id")

    cinemas_list = []

    cinema1 = None
    cinema2 = None
    cinema3 = None
    cinema4 = None
    cinema5 = None
    cinema6 = None
    cinema7 = None

    for row in c:
        (a, b, c2, d, e, f, g, h) = row
        cine = "cinema" + str(a)
        this_film = [f"{c2} : {d}, {e}, {f}"]
        if cine == 'cinema1':
            if cinema1 is None:
                cinema1 = Cinema(a, b, g, h)
                cinema1.films.append(this_film)
                cinemas_list.append(cinema1)
            else:
                cinema1.films.append(this_film)
        if cine == 'cinema2':
            if cinema2 is None:
                cinema2 = Cinema(a, b, g, h)
                cinema2.films.append(this_film)
                cinemas_list.append(cinema2)
            else:
                cinema2.films.append(this_film)
        if cine == 'cinema3':
            if cinema3 is None:
                cinema3 = Cinema(a, b, g, h)
                cinema3.films.append(this_film)
                cinemas_list.append(cinema3)
            else:
                cinema3.films.append(this_film)
        if cine == 'cinema4':
            if cinema4 is None:
                cinema4 = Cinema(a, b, g, h)
                cinema4.films.append(this_film)
                cinemas_list.append(cinema4)
            else:
                cinema4.films.append(this_film)
        if cine == 'cinema5':
            if cinema5 is None:
                cinema5 = Cinema(a, b, g, h)
                cinema5.films.append(this_film)
                cinemas_list.append(cinema5)
            else:
                cinema5.films.append(this_film)
        if cine == 'cinema6':
            if cinema6 is None:
                cinema6 = Cinema(a, b, g, h)
                cinema6.films.append(this_film)
                cinemas_list.append(cinema6)
            else:
                cinema6.films.append(this_film)
        if cine == 'cinema7':
            if cinema7 is None:
                cinema7 = Cinema(a, b, g, h)
                cinema7.films.append(this_film)
                cinemas_list.append(cinema7)
            else:
                cinema7.films.append(this_film)

    for cin in cinemas_list:
        popup_text = f"<h3 style=\"color:#f71e5b;\">{cin.name}</h3><h5>Showing Times</h5>"
        for film in cin.films:
            popup_text += f"<tr>{film[0]}</tr><br>"
        cin.popup_text = popup_text
        html = folium.Html(cin.popup_text, script=True)
        cin.popup_html = folium.Popup(html, max_width=2650)
        cin.marker = folium.Marker([cin.lat, cin.lon], popup=cin.popup_html, icon=folium.Icon(color='#f71e5b', icon='glyphicon-facetime-video')).add_to(cinema_layer)


    # set defaults in case of errors
    longitude = -3.183051
    latitude = 55.948506
    distance = 0

    if "user-dist" in form:
        distance = form.getvalue("user-dist")
    #print(f"Name: {distance}")
    #print(f"Lat: {latitude}")
    #print(f"Lon: {longitude}")
    if int(distance) > 0:
        if "lat" in form:
            latitude = form.getvalue("lat")
        if "lon" in form:
            longitude = form.getvalue("lon")

        c, user_results_layer = user_location(c, latitude, longitude, distance, user_results_layer, cinemas_list)

    c.execute("SELECT p.ROUTE, p.STOP_ID, p.STOP, p.GEOM.sdo_point.x as lon, p.GEOM.sdo_point.y as lat from s1983906.bus_stops p")
    for row in c:
        route = row[0]
        stop_id = row[1]
        stop_name = row[2]
        lon = row[3]
        lat = row[4]
        if route == 1:
            popup_text = f"<h5 style=\"color:red;\">{stop_name}</h5>"
        if route == 2:
            popup_text = f"<h5 style=\"color:blue;\">{stop_name}</h5>"
        html = folium.Html(popup_text, script=True)
        popup = folium.Popup(html, max_width=2650)
        if route == 1:
            folium.Circle(location=[lat, lon], radius=10, tooltip=f"<h5 style=\"color:red;\">{stop_name}</h5>", color='red', weight=5, fill=True).add_to(bus_stop_layer)
            #folium.Marker([lat, lon], popup=popup, icon=folium.Icon(color='red', icon='glyphicon-record')).add_to(bus_stop_layer)
        if route == 2:
            folium.Circle(location=[lat, lon], radius=10, tooltip=f"<h5 style=\"color:blue;\">{stop_name}</h5>", color='blue', weight=5, fill=True).add_to(bus_stop_layer)
            #folium.Marker([lat, lon], popup=popup, icon=folium.Icon(color='blue', icon='glyphicon-record')).add_to(bus_stop_layer)

    c.execute("SELECT a.SHOP_ID, a.NAME, a.CATEGORY, a.OPEN, a.CLOSE, a.GEOM.sdo_point.x as lon, a.GEOM.sdo_point.y as lat from s1987402.shops a")
    for row in c:
        id = row[0]
        name = row[1]
        category = row[2]
        opentime = time(int(row[3]), 0)
        formatted_open_time = opentime.strftime("%H:%M")
        closetime = time(int(row[4]), 0).strftime("%H:%M")
        formatted_close_time = closetime
        lon = row[5]
        lat = row[6]
        popup_text = f"<h3 style=\"color:#08a332;\">{name}</h3><tr><td><h5>Opening Times</h5>{formatted_open_time} to {formatted_close_time}</td></tr>"
        html = folium.Html(popup_text, script=True)
        popup = folium.Popup(html, max_width=2650)
        folium.Marker([lat, lon], popup=popup, icon=folium.Icon(color='green', icon='glyphicon-tag')).add_to(shop_layer)

    c.execute("SELECT a.REST_ID, a.NAME, a.TYPE, a.OPEN, a.CLOSE, a.RATING, a.GEOM.sdo_point.x as lon, a.GEOM.sdo_point.y as lat from s1987402.restaurants a")
    for row in c:
        id = row[0]
        name = row[1]
        type = row[2]
        opentime = time(int(row[3]), 0)
        formatted_open_time = opentime.strftime("%H:%M")
        closetime = time(int(row[4]), 0).strftime("%H:%M")
        formatted_close_time = closetime
        rating = row[5]
        lon = row[6]
        lat = row[7]
        popup_text = f"<h3 style=\"color:#14a0e0;\">{name}</h3><tr><td><h5>Opening Times</h5>{formatted_open_time} to {formatted_close_time}</td></tr>"
        html = folium.Html(popup_text, script=True)
        popup = folium.Popup(html, max_width=2650)
        folium.Marker([lat, lon], popup=popup, icon=folium.Icon(color='blue', icon='glyphicon-cutlery')).add_to(restaurant_layer)

    c.execute(query)
    for row in c:
        display = None
        name = row[0]
        try:
            if name == "Omni Centre":
                display = cinema1
            elif name == "Dominion":
                display = cinema2
            elif name == "Cameo":
                display = cinema3
            elif name == "Filmhouse":
                display = cinema4
            elif name == "Odeon Lothian":
                display = cinema5
            elif name == "Cineworld":
                display = cinema6
            elif name == "Scotsman Filmhouse":
                display = cinema7
            else:
                continue
        except ValueError:
            print("No matching cinema...")

        html = folium.Html(display.popup_text, script=True)
        display.popup_html = folium.Popup(html, max_width=2650)
        folium.Marker(row[1:], popup=display.popup_html, icon=folium.Icon(color='purple', icon='glyphicon-ok')).add_to(results_layer)
    #    if display.geoclose == True:
#            folium.Tooltip(text==f"<h5>The {display.name} cinema is less<br> than <emp>{int(int(distance)/70)}</emp> minutes walk away</h5>",icon=folium.Icon(color='orange', icon='glyphicon-screenshot')).add_to(results)


    conn.close()

    if ch3 == 1:
        restaurant_layer.show = True
    if ch4 == 1:
        bus_layer.show = True
        bus_stop_layer.show = True
    if ch5 == 1:
        shop_layer.show = True
    if ch6 == 1:
        parking_layer.show = True
    if ch7 == 1:
        area_layer.show = True

    area_layer.add_to(map1)
    bus_layer.add_to(map1)
    bus_stop_layer.add_to(map1)
    shop_layer.add_to(map1)
    restaurant_layer.add_to(map1)
    parking_layer.add_to(map1)
    cinema_layer.add_to(map1)
    user_results_layer.add_to(map1)
    results_layer.add_to(map1)



    folium.LayerControl().add_to(map1)

    return map1.get_root().render()


if __name__ == '__main__':
    print("Content-type: text/html\n")      #  Ensures that the webpage is rendered correctly using HTML code
    render_html()
