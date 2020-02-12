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


form = cgi.FieldStorage()

edinburgh_coords = [55.948795,-3.200226]

polycolours = linear.GnBu_06.scale(0,120)
polycolours.caption = 'Areas of Edinburgh'

colours = ['green', 'blue', 'red', 'orange', 'gray', 'yellow']

style1 = {'fillColor': 'red', 'color': 'red', 'weight': 2}
style3 = {'fillColor': 'blue', 'color': 'blue', 'weight': 2}


class Cinema:

    def __init__(self, id, name, lon, lat):

        self.id = id
        self.name = name
        self.lon = lon
        self.lat = lat
        self.films = []


def render_html():
    env = Environment(loader=FileSystemLoader('.'))
    temp = env.get_template('index.html')
    inpFol = foliumMap()
    print(temp.render(map=inpFol))


def foliumMap():
    
    map1 = folium.Map(location = edinburgh_coords, tiles='openstreetmap', zoom_start = 14)

    folium.TileLayer('cartodbpositron', name="CartoDB Positron", attr='Carto DB').add_to(map1)
    folium.TileLayer('cartodbdark_matter', name="CartoDB DarkMatter", attr='Carto DB').add_to(map1)
    folium.TileLayer('stamentoner', name="Stamen Toner", attr='Stamen Toner').add_to(map1)

    plugins.LocateControl(auto_start=True).add_to(map1)

    
    area_layer = folium.FeatureGroup(name='Areas of Edinburgh')
    area_sub_group = folium.plugins.FeatureGroupSubGroup(area_layer, 'Areas')
    bus_layer = folium.FeatureGroup(name='Bus Routes')
    cinema_layer = folium.FeatureGroup(name='Cinemas')
    shop_layer = folium.FeatureGroup(name='Shops')
    restaurant_layer = folium.FeatureGroup(name='Restaurants')
    #polycolours.add_to(map1)

    with open('../../../details.txt', 'r') as f:
        pwd = f.readline().strip()
    conn = cx_Oracle.connect(f"s0092179/{pwd}@geoslearn")
    c = conn.cursor()

    c.execute("SELECT ogr_fid as id, naturalcom as name, sdo_util.to_geojson(ora_geometry) as jsongeometry FROM hoods_8307")
    jsons_4326 = []
    for row in c:
        id = int(row[0])
        colour = colours[(id%6)]
        style2 = {'fillColor': '#fc7303', 'color': colour, 'weight': 2}
        name = row[1]
        item = json.load(row[2])
        jsons_4326.append(item)
        area_id = f"area{row[0]}"
        area_name = row[1]
        #folium.GeoJson(item, name=area_id, style_function = lambda x: style2).add_to(area_layer)
        folium.Choropleth(geo_data=item, name=name, popup="popup", line_color='yellow', line_opacity=1, legend_name='Edinburgh District', fill_opacity=0.6, fill_color=polycolours(id)).add_to(area_layer)



    c.execute("SELECT OGR_FID, sdo_util.to_geojson(ora_geometry) as jsongeometry from busroutes_8307")
    for row in c:
        name = row[0]
        data = json.load(row[1])
        if name == 1:
            folium.GeoJson(data, name=name, style_function = lambda x: style1).add_to(bus_layer)
        if name == 2:
            folium.GeoJson(data, name=name, style_function = lambda x: style3).add_to(bus_layer)

    c.execute("SELECT UNIQUE a.CINEMA_ID, a.NAME, b.title, c.time1, c.time2, c.time3, a.GEOM.sdo_point.x as lon, a.GEOM.sdo_point.y as lat from s1434165.cinemas a, s1434165.films b, s1434165.cinefilmrelation c where c.film_id = b.film_id and c.cinema_id = a.cinema_id")

    cinemas_list = []

    cinema1 = None
    cinema2 = None
    cinema3 = None
    cinema4 = None
    cinema5 = None

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

    for cin in cinemas_list:
        popup_text = f"<h3>{cin.name}</h3><br>"
        for film in cin.films:
            #print(cin.name, film)
            popup_text += f"<tr>{film[0]}</tr><br>"
        cin.popup_text = popup_text
        #print(cin.popup_text)
        html = folium.Html(cin.popup_text, script=True)
        popup = folium.Popup(html, max_width=2650)
        folium.Marker([cin.lat, cin.lon], popup=popup, icon=folium.Icon(color='blue', icon='glyphicon-facetime-video')).add_to(cinema_layer)

    c.execute("SELECT a.SHOP_ID, a.NAME, a.CATEGORY, a.OPEN, a.CLOSE, a.GEOM.sdo_point.x as lon, a.GEOM.sdo_point.y as lat from s1987402.shops a")
    for row in c:
        id = row[0]
        name = row[1]
        category = row[2]
        opentime = row[3]
        closetime = row[4]
        lon = row[5]
        lat = row[6]
        folium.Marker([lat, lon], popup=f"{name} Opening Time: {opentime}\n Closing Time: {closetime}", icon=folium.Icon(color='green', icon='glyphicon-tag')).add_to(shop_layer)

    c.execute("SELECT a.REST_ID, a.NAME, a.TYPE, a.OPEN, a.CLOSE, a.RATING, a.GEOM.sdo_point.x as lon, a.GEOM.sdo_point.y as lat from s1987402.restaurants a")
    for row in c:
        id = row[0]
        name = row[1]
        type = row[2]
        opentime = row[3]
        closetime = row[4]
        rating = row[5]
        lon = row[6]
        lat = row[7]
        folium.Marker([lat, lon], popup=f"{name}\nOpening Time: {opentime}\nClosing Time: {closetime}\nRating: {rating}", icon=folium.Icon(color='red', icon='glyphicon-cutlery')).add_to(restaurant_layer)

    conn.close()

    area_layer.add_to(map1)
    area_sub_group.add_to(map1)
    bus_layer.add_to(map1)
    cinema_layer.add_to(map1)
    shop_layer.add_to(map1)
    restaurant_layer.add_to(map1)
    
    #minimap = plugins.MiniMap()
    #map1.add_child(minimap)

    folium.LayerControl().add_to(map1)

    return map1.get_root().render()


if __name__ == '__main__':
    print("Content-type: text/html\n")      #  Ensures that the webpage is rendered correctly using HTML code
    render_html()
