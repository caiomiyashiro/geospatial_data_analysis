import geopandas as gpd
import json
import folium
from shapely.geometry import LineString

# TODO: Add documentation to ALL functions
def plot_linestring(geometry, speed_color=None, config=None):
    if (type(geometry) == LineString):
        geometry = gpd.GeoSeries(geometry)
    # set initial coords as first point of first linestring
    geometry_ = geometry.geometry[0]
    initial_coords = [geometry_.xy[1][0], geometry_.xy[0][0]]

    map_ = folium.Map(initial_coords, zoom_start=14)

    traces_json = json.loads(geometry.to_json())

    traces = folium.features.GeoJson(traces_json)
    map_.add_child(traces)
    return map_
