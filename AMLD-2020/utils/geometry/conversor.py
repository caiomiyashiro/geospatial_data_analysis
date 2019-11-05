from shapely.geometry import LineString
from shapely.geometry import Point
from geopandas import GeoSeries


def latlon2linestring(lat, lon):
    return GeoSeries(LineString([[lon, lat] for lat, lon in zip(lat, lon)]))

def linestring2latlon(linestring):
    return [elem.xy for elem in t.values]

def latlon2n_points(lats, lons):
    return GeoSeries([Point([lat, lon]) for lat, lon in zip(lats,lons)])
