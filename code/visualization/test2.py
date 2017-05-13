from bokeh.plotting import Figure, ColumnDataSource, show, vplot
from bokeh.io import output_file
from bokeh.models import (Slider, CustomJS, GMapPlot, 
                          GMapOptions, DataRange1d, Circle, Line)
import numpy as np

output_file("path.html")

# Create path around roundabout
r = 0.000192

x1 = np.linspace(-1,1,100)*r
x2 = np.linspace(1,-1,100)*r
x = np.hstack((x1,x2))

f = lambda x : np.sqrt(r**2 - x**2)

y1 = f(x1)
y2 = -f(x2)
y = np.hstack((y1,y2))

init_x = 40.233688
init_y = -111.646784

lon = init_x + x 
lat = init_y + y

# Initialize data sources.
location = ColumnDataSource(data=dict(x=[lon[0]], y=[lat[0]]))
path = ColumnDataSource(data=dict(x=lon, y=lat))

# Initialize figure, path, and point
"""I haven't been able to verify that the GMapPlot code below works, but 
this should be the right thing to do. The zoom may be totally wrong, 
but my latlng points should be a path around a roundabout.
"""
options = GMapOptions(lat=40.233681, lng=-111.646595, map_type="roadmap", zoom=15)
fig = GMapPlot(x_range=DataRange1d(), y_range=DataRange1d(), map_options=options)


fig = Figure(plot_height=600, plot_width=600)

c = Circle(x='x', y='y', size=10)
p = Line(x='x', y='y')

fig.add_glyph(location, c)
fig.add_glyph(path, p)

# Slider callback
callback = CustomJS(args=dict(location=location, path=path), code="""
    var loc = location.get('data');
    var p = path.get('data');

    t = cb_obj.get('value');

    /* set the point location to the path location that
       corresponds to the slider position */
    loc['x'][0] = p['x'][t];
    loc['y'][0] = p['y'][t];

    location.trigger('change');
""")

# The way I have written this, 'start' has to be 0 and 
#  'end' has to be the length of the array of path points.
slider = Slider(start=0, end=200, step=1, callback=callback)

show(vplot(fig, slider))