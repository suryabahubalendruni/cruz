import pandas as pd
import mongoengine as me
from datetime import datetime
import googlemaps
import json

from bokeh.models.widgets import TextInput, Button, Select
from bokeh.layouts import layout, widgetbox
from bokeh.io import curdoc
import sys
sys.path.append('/Users/Rishi/GitHub/cruz/cruz_bokeh')

from models import *
from plots import *

__author__ = "Surya Bahubalendruni"

def search_address(address, radius):
	geocode_response = gmaps.geocode(address)
	if len(geocode_response) != 0:
		full_address = geocode_response[0]['formatted_address']
		p_rides_df = get_pickups_nearby_df(geocode_response, radius)
		p_rides_df['type'] = 'pickup'
		d_rides_df = get_dropoffs_nearby_df(geocode_response, radius)
		d_rides_df['type'] = 'dropoff'
		rides_df = pd.concat([p_rides_df, d_rides_df], ignore_index=False)
		return rides_df, full_address
	else:
		error_message = "Malformed Google Maps API response.\nPlease try a different address, and if it still fails, check your API credentials."
		return error_message

# mongoengine connection
me.connect('cruz-dev', host='localhost', port=27017)
# google api client
google_api_keys = {
	"surya": "AIzaSyAU2gGkynk36LibmjTwLKOKMHVTRKIM87k",
	"graham": "AIzaSyBRcJ-Oj88gvz0LWNaCKg42K0K9SQIFpfs"}
gmaps = googlemaps.Client(key=google_api_keys["surya"])
with open('static/zip_coords.json') as data_file:
	zip_coords_json = json.load(data_file)

large_palette = sns_to_bokeh_palette("GnBu", 20)
medium_palette = sns_to_bokeh_palette("GnBu", 6)
small_palette = sns_to_bokeh_palette("GnBu", 2)

address = TextInput(title="Address:", value="Times Square")
month = Select(title="Month:", value="January", options= ["January", "February", "March", "April", "May", "June", "July", "August", "September",
														  "October", "November", "December"])
update = Button(label="Update", button_type="success")

rides_df, full_address = search_address(address.value, 50)
freq_dict = calc_zipcode_frequencies(zip_coords_json, rides_df)
d_choropleth, d_patches = make_choropleth_plot(zip_coords_json, freq_dict, "dropoff_frequency", large_palette)
p_choropleth, p_patches = make_choropleth_plot(zip_coords_json, freq_dict, "pickup_frequency", large_palette)
type_stacked_bar = make_stacked_bar_chart("day", 'type', rides_df, small_palette)
passenger_stacked_bar = make_stacked_bar_chart("day", 'passenger_count', rides_df, medium_palette)
# distance_violin = make_violin_plot(x="day", y="trip_distance", hue='type', data=rides_df)
# fare_violin = make_violin_plot(x="day", y="total_amount", hue='type', data=rides_df)

def update_month(attrname, old, new):
	d_choropleth.title.text = d_choropleth.title.text.split("for ")[0] + "for " + month.value
	p_choropleth.title.text = p_choropleth.title.text.split("for ")[0] + "for " + month.value
	d_patches.data_source.data['dropoff_frequency'] = freq_dict['dropoff_frequency'][month.value]
	p_patches.data_source.data['pickup_frequency'] = freq_dict['pickup_frequency'][month.value]


def update_address():
	print('hi')
	rides_df, full_address = search_address(address.value, 50)
	print('hi')
	freq_dict = calc_zipcode_frequencies(zip_coords_json, rides_df)
	d_patches.data_source.data['dropoff_frequency'] = freq_dict['dropoff_frequency'][month.value]
	p_patches.data_source.data['pickup_frequency'] = freq_dict['pickup_frequency'][month.value]
	# type_stacked_bar = make_stacked_bar_chart("day", 'type', rides_df, small_palette)
	# passenger_stacked_bar = make_stacked_bar_chart("day", 'passenger_count', rides_df, medium_palette)
	# distance_violin = make_violin_plot(x="day", y="trip_distance", hue='type', data=rides_df)
	# fare_violin = make_violin_plot(x="day", y="total_amount", hue='type', data=rides_df)


month.on_change('value', update_month)
update.on_click(update_address)
inputs = widgetbox(address, month, update)
curdoc().add_root(layout([[inputs], [d_choropleth, p_choropleth], [type_stacked_bar, passenger_stacked_bar]]))




