import geopandas as gpd
import json
import folium
from shapely.geometry import LineString

def plot_linestring(geometry):
    """
    Plot polyline(s) in Folium

    Parameters:
    geometry (shapely.geometry.LineString or geopandas.GeoSeries): polylines

    Example:
    lat = [40.732605, 40.732612, 40.732255, 40.731856, 40.731469]
    lon = [-73.99607, -73.996087, -73.996351, -73.996639, -73.996932]
    t = LineString([[lon, lat] for lat, lon in zip(lat, lon)])
    plot_linestring(t)
    """
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
