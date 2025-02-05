import folium

# coordinates for Flagstaff, Arizona
flagstaff_coords = [35.1983, -111.6513]

# create a map centered on flagstaff
arizona_map = folium.Map(location=flagstaff_coords, zoom_start=7)

# add a marker at flagstaff
folium.Marker(
    location=flagstaff_coords,
    popup="Flagstaff, Arizona",
    tooltip="Click for info"
).add_to(arizona_map)

# add a feature to let users click to add markers
arizona_map.add_child(folium.LatLngPopup())

# save the map to an html file
arizona_map.save("arizona_map.html")