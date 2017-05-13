from bokeh.io import output_file, show
from bokeh.models import (
  GMapPlot, GMapOptions, ColumnDataSource, Circle, DataRange1d, PanTool, WheelZoomTool, BoxSelectTool
)
import numpy as np
import pandas as pd 

data = pd.read_csv("boat_pos.csv")

map_options = GMapOptions(lat=34.06129, lng=126.3633, map_type="roadmap", zoom=11)

plot = GMapPlot(
    x_range=DataRange1d(), y_range=DataRange1d(), map_options=map_options
)
plot.title.text = "Austin"

# For GMaps to function, Google requires you obtain and enable an API key:
#
#     https://developers.google.com/maps/documentation/javascript/get-api-key
#
# Replace the value below with your personal API key:
plot.api_key = "AIzaSyBdIGt0H6DtEgkS7CJQF4TKXkACVnEA2W8"

source = ColumnDataSource(
    data=dict(
        lat=np.array(data['Latitude'])[::10],
        lon=np.array(data['Longitude'])[::10],
    )
)

circle = Circle(x="lon", y="lat", size=5, fill_color="blue", fill_alpha=0.8, line_color='red')
plot.add_glyph(source, circle)

plot.add_tools(PanTool(), WheelZoomTool(), BoxSelectTool())
output_file("gmap_plot.html")
show(plot)
