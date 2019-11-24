import geopandas as gpd
import json
import folium
from shapely.geometry import LineString
from folium.plugins import MarkerCluster

def plot_geometry(geometry, marker_cluster=False):
    """
    Plot geometries in Folium

    Parameters:
    geometry (shapely.geometry.LineString/Point or geopandas.GeoSeries)

    Example:
    lat = [40.732605, 40.732612, 40.732255, 40.731856, 40.731469]
    lon = [-73.99607, -73.996087, -73.996351, -73.996639, -73.996932]
    t = LineString([[lon, lat] for lat, lon in zip(lat, lon)])
    plot_linestring(t)
    """
    if (type(geometry) != gpd.GeoSeries):
        geometry = gpd.GeoSeries(geometry)

    geometry_ = geometry.geometry[0]
    initial_coords = [geometry_.xy[1][0], geometry_.xy[0][0]]

    map_ = folium.Map(initial_coords, zoom_start=14)

    geometries_json = json.loads(geometry.to_json())
    geometries_geojson = folium.features.GeoJson(geometries_json)

    if(marker_cluster == True): # exclusively for points plot
        mc = MarkerCluster()
        mc.add_child(geometries_geojson)
        map_.add_child(mc)
    else:
        map_.add_child(geometries_geojson)
    return map_
