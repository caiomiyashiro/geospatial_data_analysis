from shapely.geometry import LineString


@staticmethod
def latlon2linestring(lat, lon):
    return LineString([[lon, lat] for lat, lon in zip(lat, lon)])

@staticmethod
def linestring2latlon(linestring):
    return linestring.xy
