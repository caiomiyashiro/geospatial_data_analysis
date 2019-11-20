import pandas as pd


import requests
import numpy as np
import pandas as pd

class OSRMFramework():
    def __init__(self, OSRM_server_path):
        self.server_url = OSRM_server_path

    def route(self, lat1, lon1, lat2, lon2, max_n_routes=1):
        """
        Get route calculated by OSRM between two points

        Provided a pick up and destination, route will call the OSRM instance,
        perform the http call, extract the route, distance, duration and nodes
        and return them. OSRM will return WRONG values if pick-up OR destination
        are outside the provided OSM file and 0 if distance between pick-up
        and dropoff are irrelevant (case by case dependend)

        Parameters:
        lat1 (float): pick-up latitude
        lon1 (float): pick-up longitude
        lat2 (float): dropoff latitude
        lat2 (float): dropoff longitude
        max_n_routes (int): number of maximum routes to return if alternatives
        are found

        Returns:
        lat (array[float]): latitudes of the route points
        lon (array[float]): longitude of the route points:
        distance (int): route distance in meters
        duration (float): route duration in seconds
        osm_node_ids (array[int]): OSM node ids that are part of the calculated route

        Example:
        lat1, lon1 = 52.506327, 13.401115
        lat2, lon2 = 52.496891, 13.385983
        # after setting local osrm - https://hub.docker.com/r/osrm/osrm-backend/
        osm = OSRMFramework('localhost:5000')
        lat, lon, distance, duration, osm_node_ids = osm.route(lat1, lon1, lat2, lon2)
        """
        SERVICE = 'route'
        optionals = {'geometries': 'geojson', 'annotations':'true', 'overview':'full'}

        long_lat1 = [lon1, lat1]
        long_lat2 = [lon2, lat2]
        coords = [long_lat1, long_lat2]
        coords = ';'.join([f'{lon},{lat}' for lon, lat in coords])

        optionals_str = '?'
        for k, v in optionals.items():
            optionals_str += f'{k}={v}&'
        optionals = optionals_str[:-1]

        query = f'http://{self.server_url}/{SERVICE}/v1/driving/{coords}{optionals}'
        # print(f'query: {query}')
        response = requests.get(query).json()

        if(response['code'] == 'Ok'):
            main_route = response['routes'][0]
            coordinates = [long_lat1] + main_route['geometry']['coordinates']
            distance = main_route['distance']
            duration = main_route['duration']

            lat = [elem[1] for elem in coordinates]
            lon = [elem[0] for elem in coordinates]

            osm_node_ids = main_route['legs'][0]['annotation']['nodes']

            return lat, lon, distance, duration, osm_node_ids
        else:
            return np.nan, np.nan, np.nan, np.nan, np.nan

    # TODO: Interpolate timestamps in case of new nodes being created on map matching, e.g., new corner nodes
    def match(self, lat, lon, timestamps=None, radiuses=None):
        """
        Snaps GPS traces to the street thought map matching

        Provided a sequence of lat/lon representing a GPS trace, match will
        snap this segment to the street, i.e., to OSM street node ids.

        Parameters:
        lat (array[float]): sequence of latitudes
        lon (array[float]): sequence of longitudes
        timestamps (array[int]): UNIX timestamps associated to each GPS point
        radiuses (array[int]): accuracy associated to each GPS point

        Returns:lat, lon, node_id_list
        lat (array[float]): latitudes of the route points
        lon (array[float]): longitude of the route points
        node_id_list (array[int]): list of matched OSM node ids

        Example:
        lat = [52.51156939,52.51148186,52.51102356,52.51077686,52.51063361,52.51046813,52.51030345,52.51013817,52.50997492,52.50980902,
               52.50978678,52.50981555,52.50984412,52.50986943,52.50989677,52.50989554,52.50985494,52.50976862,52.50968128,52.50960578]
        lon = [13.37081563, 13.37085016, 13.37053299, 13.36909533, 13.36821422, 13.36722583, 13.36624146, 13.36526077, 13.3642878, 13.36323738,
               13.36231135, 13.36137023, 13.36044654, 13.35955068, 13.35856128, 13.35757691, 13.35658886, 13.355578  , 13.3546114 , 13.35361328]
        timestamps = ['2019-05-31 06:04:46', '2019-05-31 06:04:56','2019-05-31 06:05:06', '2019-05-31 06:05:16','2019-05-31 06:05:21',
                      '2019-05-31 06:05:26','2019-05-31 06:05:31', '2019-05-31 06:05:36','2019-05-31 06:05:41', '2019-05-31 06:05:46',
                      '2019-05-31 06:05:51', '2019-05-31 06:05:56','2019-05-31 06:06:01', '2019-05-31 06:06:06','2019-05-31 06:06:11',
                      '2019-05-31 06:06:16','2019-05-31 06:06:21', '2019-05-31 06:06:26','2019-05-31 06:06:31', '2019-05-31 06:06:36']
        radiuses = [5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5.]
        osm = OSRMFramework('localhost:5000')
        lat, lon, nodes_id = osm.match(lat, lon, timestamps, radiuses)
        """
        SERVICE = 'match'
        optionals = {'geometries': 'geojson', 'annotations':'nodes'}

        if (timestamps is not None):
            timestamp_unix = pd.to_datetime(timestamps, format='%Y-%M-%d %H:%m:%S').strftime('%s')
            timestamp_unix = ';'.join(timestamp_unix)
            optionals['timestamps'] = timestamp_unix

        if (radiuses is not None):
            # increase chance of finding correct candidate by doubling std (95% chance)
            RADIUS_TOLERANCE_MULT = 1
            radiuses = np.array(radiuses * RADIUS_TOLERANCE_MULT).astype(str)
            radiuses = ';'.join(radiuses)
            optionals['radiuses'] = radiuses

        optionals_str = '?'
        for k, v in optionals.items():
            optionals_str += f'{k}={v}&'
        optionals = optionals_str[:-1]  # remove last "&"

        coords = [[lon_, lat_] for lon_, lat_ in zip(lon, lat)]
        coords_str = ';'.join([f'{lon},{lat}' for lon, lat in coords])

        query = f'http://{self.server_url}/{SERVICE}/v1/driving/{coords_str}{optionals}'

        response = requests.get(query).json()
        if (response['code'] == 'Ok'):
            match_coords = response['matchings'][0]['geometry']['coordinates']

            lon = [elem[0] for elem in match_coords]
            lat = [elem[1] for elem in match_coords]

            nodes = []
            for leg in response['matchings'][0]['legs']:
                nodes.extend(leg['annotation']['nodes'])
            node_id_list = pd.Series(nodes).drop_duplicates(keep='first').values

            return lat, lon, node_id_list
        else:
            raise Exception(f"Error in Mapmatching: {response['code']}")
