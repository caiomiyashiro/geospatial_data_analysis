from shapely.geometry import LineString
from shapely.geometry import Point
from geopandas import GeoSeries

def latlon2linestring(lat, lon):
    """
    convert sequence of latitudes and longitudes to a geometry

    Parameters:
    lat (array[float]): latitudes of the polyline
    lon (array[float]): longitude of the polyline

    Return:
    GeoSeries: converted geometry
    """
    return GeoSeries(LineString([[lon, lat] for lat, lon in zip(lat, lon)]))

def linestring2latlon(linestring):
    """
    convert polyline geometry to sequence of latitudes and longitudes

    Parameters:
    linestring (shapely.geometry.LineString): polyline geometry

    Return:
    array[2, float]: array of latitudes and longitudes
    """
    return [elem.xy for elem in t.values]

def latlon2n_points(lats, lons):
    """
    convert sequence of latitudes and longitudes to a sequence of geometry points

    Parameters:
    lat (array[float]): latitudes of the polyline
    lon (array[float]): longitude of the polyline

    Return:
    GeoSeries: converted points geometry
    """
    return GeoSeries([Point([lat, lon]) for lat, lon in zip(lats,lons)])
