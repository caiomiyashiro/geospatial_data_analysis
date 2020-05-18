import pandas as pd
import requests
import osmnx as ox
import numpy as np
import networkx as nx
import pickle
from itertools import combinations
from helpers import np_distance_haversine


class OSRMFramework:
    def __init__(self, OSRM_server_path):
        self.server_url = OSRM_server_path

    def nearest(self, lat, lon):
        SERVICE = "nearest"
        optionals = {"number": 1}
        coord = f"{lon},{lat}"

        optionals_str = "?"
        for k, v in optionals.items():
            optionals_str += f"{k}={v}&"
        optionals = optionals_str[:-1]

        query = f"http://{self.server_url}/{SERVICE}/v1/driving/{coord}{optionals}"
        # print(f"query: {query}")
        response = requests.get(query).json()

        if response["code"] == "Ok":
            waypoint = response["waypoints"][0]
            lon_node, lat_node = waypoint["location"]
            name_node = waypoint["name"]
            id_node = waypoint["nodes"][1]

            return id_node, lat_node, lon_node, name_node
        else:
            return np.nan, np.nan, np.nan, np.nan

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
        SERVICE = "route"
        optionals = {"geometries": "geojson", "annotations": "true", "overview": "full"}

        long_lat1 = [lon1, lat1]
        long_lat2 = [lon2, lat2]
        coords = [long_lat1, long_lat2]
        coords = ";".join([f"{lon},{lat}" for lon, lat in coords])

        optionals_str = "?"
        for k, v in optionals.items():
            optionals_str += f"{k}={v}&"
        optionals = optionals_str[:-1]

        query = f"http://{self.server_url}/{SERVICE}/v1/driving/{coords}{optionals}"
        # print(f'query: {query}')
        response = requests.get(query).json()

        if response["code"] == "Ok":
            main_route = response["routes"][0]
            coordinates = [long_lat1] + main_route["geometry"]["coordinates"]
            distance = main_route["distance"]
            duration = main_route["duration"]

            lat = [elem[1] for elem in coordinates]
            lon = [elem[0] for elem in coordinates]

            osm_node_ids = main_route["legs"][0]["annotation"]["nodes"]

            return lat, lon, distance, duration, osm_node_ids
        else:
            return np.nan, np.nan, np.nan, np.nan, np.nan

    # Allow option to not return/process lat_lon from the route - just obtain distance/duration
    def batch_route(self, lon_lat_list):

        # coords = [[-73.996070, 40.732605], [-73.980675, 40.761864], [-73.977640, 40.752346], [-73.970390, 40.768867]]
        coords_str = ";".join([f"{lon},{lat}" for lon, lat in lon_lat_list])

        optionals = {"geometries": "geojson", "annotations": "true", "overview": "full", "steps": "false"}
        optionals_str = "?"
        for k, v in optionals.items():
            optionals_str += f"{k}={v}&"
        optionals = optionals_str[:-1]

        query = f"http://{self.server_url}/route/v1/driving/{coords_str}{optionals}"
        response = requests.get(query).json()

        if response["code"] == "Ok":
            response_route = np.array(response['routes'][0]['geometry']['coordinates'])

            mapped_coords_ix = []
            for coord_lon_lat in lon_lat_list:
                distances_to_point = np_distance_haversine(lat1=response_route[:, 1],
                                                           lon1=response_route[:, 0],
                                                           lat2=np.ones(len(response_route)) * coord_lon_lat[1],
                                                           lon2=np.ones(len(response_route)) * coord_lon_lat[0])
                mapped_coords_ix.append(np.argmin(distances_to_point))

            lat = []
            lon = []
            for i in np.arange(len(mapped_coords_ix) - 1, step=2):
                route_segment = np.array(response_route[mapped_coords_ix[i]:mapped_coords_ix[i + 1] - 1])
                lat.append(route_segment[:, 1])
                lon.append(route_segment[:, 0])

            ######

            distance = []
            duration = []
            osm_node_ids = []
            legs = response['routes'][0]['legs']
            for i in np.arange(len(legs), step=2):
                distance.append(legs[i]['distance'])
                duration.append(legs[i]['duration'])
                osm_node_ids.append(legs[i]['annotation']['nodes'])

            return lat, lon, distance, duration, osm_node_ids
        else:
            na_array = [np.nan]*len(lon_lat_list)/2
            return na_array, na_array, na_array, na_array, na_array

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
        SERVICE = "match"
        optionals = {"geometries": "geojson", "annotations": "nodes"}

        if timestamps is not None:
            timestamp_unix = pd.to_datetime(
                timestamps, format="%Y-%M-%d %H:%m:%S"
            ).strftime("%s")
            timestamp_unix = ";".join(timestamp_unix)
            optionals["timestamps"] = timestamp_unix

        if radiuses is not None:
            # increase chance of finding correct candidate by doubling std (95% chance)
            RADIUS_TOLERANCE_MULT = 1
            radiuses = np.array(radiuses * RADIUS_TOLERANCE_MULT).astype(str)
            radiuses = ";".join(radiuses)
            optionals["radiuses"] = radiuses

        optionals_str = "?"
        for k, v in optionals.items():
            optionals_str += f"{k}={v}&"
        optionals = optionals_str[:-1]  # remove last "&"

        coords = [[lon_, lat_] for lon_, lat_ in zip(lon, lat)]
        coords_str = ";".join([f"{lon},{lat}" for lon, lat in coords])

        query = f"http://{self.server_url}/{SERVICE}/v1/driving/{coords_str}{optionals}"

        response = requests.get(query).json()
        if response["code"] == "Ok":
            match_coords = response["matchings"][0]["geometry"]["coordinates"]

            lon = [elem[0] for elem in match_coords]
            lat = [elem[1] for elem in match_coords]

            nodes = []
            for leg in response["matchings"][0]["legs"]:
                nodes.extend(leg["annotation"]["nodes"])
            node_id_list = pd.Series(nodes).drop_duplicates(keep="first").values

            return lat, lon, node_id_list
        else:
            raise Exception(f"Error in Mapmatching: {response['code']}")

    def split_close_tours(
        self,
        df,
        pickup_lat_col,
        pickup_lon_col,
        dropoff_lat_col,
        dropoff_lon_col,
        threshold_km=0.3,
    ):

        all_tours_distant = False
        df_ind_tours = pd.DataFrame()

        df_2 = df.copy()
        while all_tours_distant != True:
            df_2[[f"{pickup_lat_col}_shift", f"{pickup_lon_col}_shift"]] = df_2[
                [pickup_lat_col, pickup_lon_col]
            ].shift(-1)
            df_2["distance_next_point"] = np_distance_haversine(
                lat1=df_2[dropoff_lat_col],
                lon1=df_2[dropoff_lon_col],
                lat2=df_2[f"{pickup_lat_col}_shift"],
                lon2=df_2[f"{pickup_lon_col}_shift"],
            )

            is_close_index = df_2.loc[df_2["distance_next_point"] < threshold_km].index
            if len(is_close_index) == 0:
                all_tours_distant = True
            else:
                df_ind_tours = pd.concat(
                    [df_ind_tours, df_2.loc[df_2.index.isin(is_close_index)]]
                )
                df_2 = df_2.loc[~df_2.index.isin(is_close_index)]
        cols_to_remove = [
            f"{pickup_lat_col}_shift",
            f"{pickup_lon_col}_shift",
            "distance_next_point",
        ]
        return (
            df_2.drop(cols_to_remove, axis=1),
            df_ind_tours.drop(cols_to_remove, axis=1),
        )


class RouteAnnotator:

    # TODO add different forms of network retrieval from OSMNx
    def __init__(self, place, network_type="drive_service"):

        self.segment_lookup_ = None
        self.way_lookup_ = None
        self.node_lookup_ = None
        self.G = None
        self.place = place
        self.network_type = network_type

        self.HIGHWAY_SPEED_LIMITS = {  # copied from https://github.com/Project-OSRM/osrm-backend/blob/master/profiles/car.lua
            "motorway": 90,
            "motorway_link": 45,
            "trunk": 85,
            "trunk_link": 40,
            "primary": 65,
            "primary_link": 30,
            "secondary": 40,  # original: 55 - changed to NY where secondary = 25 mph ~= 40 kmh
            "secondary_link": 25,
            "tertiary": 40,
            "tertiary_link": 20,
            "unclassified": 25,
            "residential": 40,
            "living_street": 10,
            "service": 15,
            "footway": 4,  # custom
            "path": 4,  #
            "pedestrian": 4,  #
            "steps": 2,  #
            "track": 4,  #
            "piste": 4,  #
            "corridor": 4,  #
            "bridleway": 4,  #
            "razed": 4,  #
            "elevator": 0.2,  #
        }

    def build_lookups(self):
        # example - 'new york, usa'
        self.G = ox.graph_from_place(
            self.place, network_type=self.network_type, simplify=False
        )
        self.add_speeds()
        self._build_lookups()

    def add_speeds(self):
        """
        Loops through edges and connecting nodes and extract speed limit given
        tag or highway type. If tag is not present, use highway type
        """

        for u, v, k, data in self.G.edges(data=True, keys=True):
            if (
                "maxspeed" in data
                and type(data["maxspeed"]) == str
                and data["maxspeed"].isdigit()
            ):
                continue
            else:
                if (
                    type(data["highway"]) == list
                ):  # sometimes data['highway'] comes with a list
                    cond = [
                        elem in self.HIGHWAY_SPEED_LIMITS for elem in data["highway"]
                    ]
                    highway_type = data["highway"][np.where(cond)[0][0]]
                else:
                    highway_type = data["highway"]

                if highway_type in self.HIGHWAY_SPEED_LIMITS:
                    speed = self.HIGHWAY_SPEED_LIMITS[highway_type]
                    data["maxspeed"] = speed

    def _build_lookups(self):
        """
        Loops through edges and connecting nodes build three lookup dictionaries:
            - segment_lookup: return the way id given two nodes. It can return
            ways even if provided nodes are not sequentially connected
            - way_lookup: return way metadata given the way id
            - node_lookup: return node metadata given the node id
        """
        # build segment lookup
        segment_lookup = {}
        segment_lengths = {}
        way2nodes = {}
        way2nodes_pair = {}
        way_lookup = {}
        way_segment_lengths = {}
        node_lookup = {}

        # build segment lookup
        for u, v, k, data in self.G.edges(data=True, keys=True):

            if type(data["osmid"]) != list:
                way_ids = [data["osmid"]]
            else:
                way_ids = data["osmid"]

            for way in way_ids:
                if way not in way2nodes.keys():
                    way2nodes[way] = []
                    way2nodes_pair[way] = []
                    way_lookup[way] = data
                    way_segment_lengths[way] = []
                way2nodes[way].extend([u, v])  # add all nodes associated to a way
                way2nodes_pair[way].append(
                    [u, v]
                )  # add pair of nodes belonging to way id
                way_segment_lengths[way].append(
                    data["length"]
                )  # collect way lengths to sum up afterwards

            if (
                u not in segment_lengths.keys()
            ):  # store each node-node direct segment length.
                segment_lengths[u] = {}  # NOT DOING ANYTHING WITH IT FOR NOW
            segment_lengths[u][v] = data["length"]

        # 1st FOR, build node id sequence belonging to way_id
        # 2nd FOR, sum segments lengths and add node id list to way lookup
        final_node_sequence = {}
        for (
            way_id,
            values,
        ) in way2nodes_pair.items():  # key: way_id, values: pairs of node ids
            relations = {}
            for pair in values:  # build dict - key: node_pre - value: node post
                relations[pair[0]] = pair[1]
            keys = relations.keys()
            values_ = relations.values()  # if a key (node_pre) doesn't exist in values
            begin_key = list(
                keys - values_
            )  # it means it has only origin = way initial node

            if len(values) > 1 and len(begin_key) == 1:  # if NOT cyclic sequence?
                begin_key = begin_key[0]
                node_sequence = [begin_key]
                val = relations[begin_key]
                try:
                    while (
                        val not in node_sequence
                    ):  # run through `relations` finding the node sequence pair by pair
                        node_sequence.append(val)
                        count += 1
                        begin_key = val
                        val = relations[begin_key]
                except Exception as e:  # until a pair is not found in the dict anymore = exception
                    e  # do nothing in exception
                final_node_sequence[
                    way_id
                ] = node_sequence  # and store node "ordered" list as a Way metadata
            else:
                final_node_sequence[way_id] = (
                    list(keys)[0] + list(values_)[0]
                )  # if way has only 1 node, store it as it is

        for key, value in way_lookup.items():
            way_lookup[key]["length"] = np.sum(way_segment_lengths[key])
            way_lookup[key]["node_sequence"] = final_node_sequence[key]

        # build dict: key1: node1, key2: node2, value: way_id between ALL pair of nodes id IN way
        nodes2way = {}
        for key, values in way2nodes.items():
            for pair in combinations(values, 2):
                if pair[0] not in nodes2way.keys():
                    nodes2way[pair[0]] = {}
                nodes2way[pair[0]][pair[1]] = key

        # build dict key1: node_id, value: node_metadata
        for node in self.G.nodes(data=True):
            node_lookup[node[0]] = node[1]

        self.segment_lookup_ = nodes2way
        self.way_lookup_ = way_lookup
        self.node_lookup_ = node_lookup

    def segment_lookup(self, node_id_list):
        """
        Get way id given pair of node ids.

        Provided a sequence of node ids, segment_lookup will iterate over it
        pair by pair and check the pair in the lookup table. Even though two
        nodes are not directly connected in OSM, this function will return way_id
        if both nodes belong to the way.

        Parameters:
        node_id_list (array[int]): node id list.

        Returns:
        nodes_lookup (array[int]): return ways connecting the nodes. Given
        node_id_list = [1,2,3], segment_lookup will return a list of size 2
        giving the ways that connect nodes [1,2] and [2,3] and so on.
        """
        if type(node_id_list) == int:
            return self.segment_lookup_[node_id_list[i]][node_id_list[i + 1]]
        else:
            ways_id = []
            i = 0
            while i < len(node_id_list) - 1:
                ways_id.append(
                    self.segment_lookup_[node_id_list[i]][node_id_list[i + 1]]
                )
                i += 1
            return ways_id

    def way_lookup(self, way_id_list):
        """
        Get way metadata given way id

        Provided a sequence of way ids, way_lookup will iterate over them
        individually and return the way metadata of each in a dictionary

        Parameters:
        way_id_list (array[int]): way id list.

        Returns:
        ways_lookup (array[dict]): return ways' metadata in array
        """
        if type(way_id_list) == int:
            return self.way_lookup_[way_id_list]
        else:
            ways_lookup = []
            for way in way_id_list:
                ways_lookup.append(self.way_lookup_[way])
            return ways_lookup

    def node_lookup(self, node_id_list):
        """
        Get node_lookup metadata given node id

        Provided a sequence of node ids, node_lookup will iterate over them
        individually and return the node metadata of each in a dictionary

        Parameters:
        node_id_list (array[int]): node id list.

        Returns:
        nodes_lookup (array[dict]): return nodes' metadata in array
        """
        if type(node_id_list) == int:
            return self.node_lookup_[node_id_list]
        else:
            nodes_lookup = []
            for node in node_id_list:
                nodes_lookup.append(self.node_lookup_[node])
            return nodes_lookup

    @staticmethod
    def AMLD_local_lookups(place, network_type="drive_service"):
        """
        Build RouteAnnotator and load local lookup dictionaries

        OSMnx download the whole city network before processing and this
        takes a lot of memory. For the AMLD presentation, we load already saved
        dictionaries as downloading the network was breaking Docker container

        Parameters:
        place (str): place to be inverse geocoded by nominatin in OSMnx
        network_type (str): type of network. Check OSMnx

        Returns:
        ra (RouteAnnotator): object with loaded lookups
        """
        ra = RouteAnnotator(place, network_type)
        with open("data/AMLD_lookups.pickle", "rb") as f:
            node_lookup_, segment_lookup_, way_lookup_ = pickle.load(f)
        ra.node_lookup_ = node_lookup_
        ra.segment_lookup_ = segment_lookup_
        ra.way_lookup_ = way_lookup_
        return ra

def run_osrm_docker(
    osrm_files_path: str, place_name: str, traffic_file_name: str = None, download_pbf: bool = True
) -> str:
    """ Run a custom osrm-backend container..

        NOTE: as number of bins are fixed, it's size depends on the data range. Outliers can create huge bins and they will
        not show up in the plot. The same is valid for KDE, if one outlier point is estimated, all the distribution mass
        has to reach there, which will bring the whole curve to a flat.

        NOTE: pyplot figure is not closed, plot can be adapted after this function finishes

        :param data_source_1: data points 1
        :param data_source_2: data points 2
        :param plot_1_type: one of ['density', 'histogram'] for data source 1
        :param plot_2_type: one of ['density', 'histogram'] for data source 2
        :param plot_config: plt.plot parameters as dictionary. Check 'plot_properties' for available features
        :param axis: pyplot axis. Usually created by plt.subplots(nrow, ncol) and plot subplots
        """
    # os.system("docker pull osrm/osrm-backend:v5.22.0")
    pbf_city2url = {
        "hamburg": [
            "http://download.geofabrik.de/europe/germany/hamburg-latest.osm.pbf",
            "http://download.geofabrik.de/europe/germany/schleswig-holstein-latest.osm.pbf",
            "http://download.geofabrik.de/europe/germany/niedersachsen-latest.osm.pbf",
        ],
        "berlin": "http://download.geofabrik.de/europe/germany/brandenburg-latest.osm.pbf",
        "munich": "http://download.geofabrik.de/europe/germany/bayern-latest.osm.pbf",
        "frankfurt": "http://download.geofabrik.de/europe/germany/hessen-latest.osm.pbf",
        "warsaw": "http://download.geofabrik.de/europe/poland-latest.osm.pbf",
        "dublin": "http://download.geofabrik.de/europe/ireland-and-northern-ireland-latest.osm.pbf",
        "madrid": "http://download.geofabrik.de/europe/spain-latest.osm.pbf",
        "barcelona": "http://download.geofabrik.de/europe/spain-latest.osm.pbf",
        "london": "http://download.geofabrik.de/europe/great-britain-latest.osm.pbf",
        "rome": "http://download.geofabrik.de/europe/italy-latest.osm.pbf",
        "bucharest": "http://download.geofabrik.de/europe/romania-latest.osm.pbf",
    }
    place_name = place_name.lower()
    if download_pbf:
        if not os.path.isfile(f"{osrm_files_path}/{place_name}.osm.pbf"):
            pbf_url = pbf_city2url[place_name]
            print(f"\nDownloading pbf file for {place_name} at {pbf_url}")
            if place_name != "hamburg":
                r = requests.get(pbf_url)
                with open(f'{osrm_files_path}/{place_name}.osm.pbf', 'wb') as f:
                    f.write(r.content)
            else:
                i = 1
                for pbf_url_ in pbf_url:
                    r = requests.get(pbf_url_)
                    with open(f'{osrm_files_path}/hamburg_{i}.osm.pbf', 'wb') as f:
                        f.write(r.content)
                    i += 1
                os.system(f"osmium merge {osrm_files_path}/hamburg_1.osm.pbf {osrm_files_path}/hamburg_2.osm.pbf"
                          + f" -o {osrm_files_path}/hh-sh.osm.pbf")
                os.remove(f"{osrm_files_path}/hamburg_1.osm.pbf")
                os.remove(f"{osrm_files_path}/hamburg_2.osm.pbf")
                os.system(f"osmium merge {osrm_files_path}/hh-sh.osm.pbf {osrm_files_path}/hamburg_3.osm.pbf"
                          + f" -o {osrm_files_path}/hamburg.osm.pbf")
                os.remove(f"{osrm_files_path}/hh-sh.osm.pbf")
                os.remove(f"{osrm_files_path}/hamburg_3.osm.pbf")
        else:
            print(f"File {osrm_files_path}/{place_name}.osm.pbf already exists.")

    print(f"\nExtracting graph data... at {osrm_files_path}")
    command = f"docker run -t -v {osrm_files_path}:/data osrm/osrm-backend osrm-extract "\
              + f"-p /opt/car.lua /data/{place_name}.osm.pbf"
    print(command)
    os.system(command)

    print("Partitioning graph data...")
    command = f"docker run -t -v {osrm_files_path}:/data osrm/osrm-backend osrm-partition /data/{place_name}.osm"
    print(command)
    os.system(command)

    print("Customising graph data...")
    if traffic_file_name is not None:
        traffic_file_str = f"--segment-speed-file /data/{traffic_file_name}"
    else:
        traffic_file_str = ""
    command = f"docker run -t -v {osrm_files_path}:/data osrm/osrm-backend " \
             + f"osrm-customize /data/{place_name}.osm {traffic_file_str}"
    print(command)
    os.system(command)

    print("Running Router...")
    command = f"docker run --name python_docker_{place_name} -d -t -i -p 5000:5000 " \
              + f"-v {osrm_files_path}:/data osrm/osrm-backend osrm-routed --algorithm mld /data/{place_name}.osm"
    print(command)
    os.system(command)

    return f"python_docker_{place_name}"


def stop_python_osrm(container_name: str) -> None:
    """Stop the newly created osrm-backend container."""
    os.system(f"docker stop {container_name}")
    os.system(f"docker rm {container_name}")
