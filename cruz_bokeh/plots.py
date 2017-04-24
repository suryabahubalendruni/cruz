import pandas as pd
from datetime import datetime
from bokeh import mpl
from bokeh.charts.attributes import cat
from bokeh.charts import Bar
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, LogColorMapper, ColorBar, NumeralTickFormatter, FuncTickFormatter, PrintfTickFormatter
import seaborn as sns

def sns_to_bokeh_palette(sns_palette, count):
	palette = []
	for tup in sns.color_palette(sns_palette, count):
		red, green, blue = tup
		red *= 255
		green *= 255
		blue *= 255
		palette.append('#%02x%02x%02x' % (int(round(red)), int(round(green)), int(round(blue))))
	return palette

def calc_zipcode_frequencies(zip_json, data, start_month="January", end_month="July"):
	months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

	freq_dict = {"pickup_frequency": {}, "dropoff_frequency": {}}

	for i, month in enumerate(months[months.index(start_month):months.index(end_month) + 1]):

		p_query = (
			(datetime(2015, i + 1, 1) < data['pickup_datetime']) & (data['pickup_datetime'] < datetime(2015, i + 2, 1)) & (data['type'] == 'dropoff'))
		if True in p_query.values:
			p_freq = pd.DataFrame(100 * data[p_query]['pickup_zipcode'].value_counts() / sum(p_query))
			freq_dict['pickup_frequency'][month] = p_freq.reindex(zip_json['zipcode']).fillna(0.0)['pickup_zipcode'].tolist()
		else:
			freq_dict['pickup_frequency'][month] = [0.0] * 262

		d_query = (
			(datetime(2015, i + 1, 1) < data['dropoff_datetime']) & (data['dropoff_datetime'] < datetime(2015, i + 2, 1)) & (
				data['type'] == 'pickup'))
		if True in d_query.values:
			d_freq = pd.DataFrame(100 * data[d_query]['dropoff_zipcode'].value_counts() / sum(d_query))
			freq_dict['dropoff_frequency'][month] = d_freq.reindex(zip_json['zipcode']).fillna(0.0)['dropoff_zipcode'].tolist()
		else:
			freq_dict['dropoff_frequency'][month] = [0.0] * 262

	return freq_dict


def make_choropleth_plot(zip_data, freq_dict, weight, palette, start_month="January", width=500, height=500):
	data = zip_data
	data[weight] = freq_dict[weight][start_month]
	source = ColumnDataSource(data)

	TOOLS = "pan,wheel_zoom,box_zoom,reset,hover,save"
	title = "{0} Choropleth for {1}".format("Destination" if weight == "dropoff_frequency" else "Origin", start_month)

	choropleth = figure(title=title, tools=TOOLS, x_axis_location=None, y_axis_location=None, responsive=True,
						plot_width=width, plot_height=height, toolbar_location="above", toolbar_sticky=False)
	choropleth.grid.grid_line_color = "SlateGray"
	choropleth.grid.grid_line_alpha = .5
	choropleth.grid.minor_grid_line_color = "SlateGray"
	choropleth.grid.minor_grid_line_alpha = .2

	freq_max = 0
	for freq_list in freq_dict[weight].values():
		freq_max = max(freq_list) if max(freq_list) > freq_max else freq_max

	color_mapper = LogColorMapper(palette=palette, high=freq_max, low=0.0)
	patches = choropleth.patches('longitude', 'latitude', source=source, fill_color={'field': weight, 'transform': color_mapper}, fill_alpha=.9,
								 line_color="black", line_width=.6)
	color_bar = ColorBar(color_mapper=color_mapper, label_standoff=12, border_line_color=None, location=(0, 0))
	choropleth.add_layout(color_bar, 'right')

	hover = choropleth.select_one(HoverTool)
	hover.point_policy = "follow_mouse"
	hover.tooltips = [
		("Name", "@name"),
		("Zipcode", "@zipcode"),
		("Borough", "@borough"),
		(weight.replace("_", " ").title(), "@{0}%".format(weight)),
		("(Long, Lat)", "($x.2, $y.2)")
	]

	return choropleth, patches


def make_stacked_bar_chart(buckets, stack, data, palette, width=500, height=500):
	cp = data
	if buckets == "day":
		cp[buckets] = cp.apply(lambda row: row['pickup_datetime'].weekday(), axis=1)
	elif buckets == "month":
		cp[buckets] = cp.apply(lambda row: row['pickup_datetime'].month, axis=1)
	TOOLS = "pan,reset,hover,save"
	stacked_bar = Bar(cp, label=buckets, values=buckets, agg='count', stack=cat(stack, sort=True), tools=TOOLS,
					  title="{0} Stacked Bar for {1}".format(("Daily" if buckets == "day" else "Monthly"), stack.replace("_", " ").title()),
					  palette=palette, plot_width=width, plot_height=height, toolbar_location="above", toolbar_sticky=False,
					  legend_sort_field='color', legend_sort_direction='ascending', responsive=True)
	hover = stacked_bar.select_one(HoverTool)
	hover.point_policy = "follow_mouse"
	hover.tooltips = [("Frequency", "@height"),
					  ("{0}".format(stack.replace("_", " ").title()), "@{0}".format(stack))
					  ]

	def day_ticker():
		days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
		if abs(int(round(tick)) - tick) < .05:
			return days[int(round(tick))]
		else:
			return ""

	def month_ticker():
		months = ["January", "February", "March", "April", "May", "June", "July"]
		if abs(int(round(tick)) - tick) < .05:
			return months[int(round(tick))]
		else:
			return ""

	if buckets == "day":
		stacked_bar.xaxis.formatter = FuncTickFormatter.from_py_func(day_ticker)
	else:
		stacked_bar.xaxis.formatter = FuncTickFormatter.from_py_func(month_ticker)
	stacked_bar.grid.grid_line_color = "SlateGray"
	stacked_bar.grid.grid_line_alpha = .5
	stacked_bar.grid.minor_grid_line_color = "SlateGray"
	stacked_bar.grid.minor_grid_line_alpha = .2

	return stacked_bar


def make_violin_plot(x, y, hue, data, plot_type="factor", palette="GnBu", width=750, height=500):
	data = data[[x, y, hue]]
	sns_palette = sns.color_palette(palette, 2)
	sns.set_style("whitegrid")
	if plot_type == "factor":
		violin_plot_sns = sns.factorplot(x=x, y=y, hue=hue, data=data, kind="violin", palette=sns_palette)
	else:
		violin_plot_sns = sns.violinplot(x=x, y=y, hue=hue, data=data, palette=sns_palette, split=True, scale="area", inner="box", orient="v",
										 bw=.15, responsive = True)
	violin_plot = mpl.to_bokeh()
	violin_plot.toolbar_location = "above"
	violin_plot.toolbar_sticky = False
	violin_plot.grid.grid_line_color = "SlateGray"
	violin_plot.grid.grid_line_alpha = .5
	violin_plot.grid.minor_grid_line_color = "SlateGray"
	violin_plot.grid.minor_grid_line_alpha = .2
	violin_plot.plot_height = height
	violin_plot.plot_width = width
	if "amount" in y:
		violin_plot.title.text = "Fare Violin Plot"
		violin_plot.yaxis[0].formatter = NumeralTickFormatter(format="$ 0.00")
	if "distance" in y:
		violin_plot.title.text = "Distance Violin Plot"
		violin_plot.yaxis[0].formatter = PrintfTickFormatter(format="%5.2f miles")

	def day_ticker():
		days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
		if abs(int(round(tick)) - tick) < .05:
			return days[int(round(tick))]
		else:
			return ""

	def month_ticker():
		months = ["January", "February", "March", "April", "May", "June", "July"]
		if abs(int(round(tick)) - tick) < .05:
			return months[int(round(tick))]
		else:
			return ""

	if "day" in x:
		violin_plot.xaxis[0].formatter = FuncTickFormatter.from_py_func(day_ticker)
	if "month" in x:
		violin_plot.xaxis[0].formatter = FuncTickFormatter.from_py_func(month_ticker)
	return violin_plot