import osmnx as ox
import numpy as np
import networkx as nx
import pickle
from itertools import combinations

class RouteAnnotator():

    # TODO add different forms of network retrieval from OSMNx
    def __init__(self, place, network_type='drive_service'):

        self.segment_lookup_ = None
        self.way_lookup_ = None
        self.node_lookup_ = None
        self.G = None
        self.place = place
        self.network_type = network_type

        self.HIGHWAY_SPEED_LIMITS ={   # copied from https://github.com/Project-OSRM/osrm-backend/blob/master/profiles/car.lua
            'motorway':90,
            'motorway_link':45,
            'trunk':85,
            'trunk_link':40,
            'primary':65,
            'primary_link':30,
            'secondary':40, # original: 55 - changed to NY where secondary = 25 mph ~= 40 kmh
            'secondary_link':25,
            'tertiary':40,
            'tertiary_link':20,
            'unclassified':25,
            'residential':40,
            'living_street':10,
            'service':15,
            'footway': 4,    # custom
            'path': 4,       #
            'pedestrian': 4, #
            'steps': 2,      #
            'track': 4,      #
            'piste': 4,      #
            'corridor': 4,   #
            'bridleway': 4,  #
            'razed': 4,      #
            'elevator': 0.2  #
        }

    def build_lookups(self):
        # example - 'new york, usa'
        self.G = ox.graph_from_place(self.place, network_type=self.network_type, simplify=False)
        self.add_speeds()
        self._build_lookups()

    def add_speeds(self):
        """
        Loops through edges and connecting nodes and extract speed limit given
        tag or highway type. If tag is not present, use highway type
        """

        for u, v, k, data in self.G.edges(data=True, keys=True):
            if 'maxspeed' in data and type(data['maxspeed']) == str and data['maxspeed'].isdigit():
                continue
            else:
                if(type(data['highway']) == list): # sometimes data['highway'] comes with a list
                    cond = [elem in self.HIGHWAY_SPEED_LIMITS for elem in data['highway']]
                    highway_type = data['highway'][np.where(cond)[0][0]]
                else:
                    highway_type = data['highway']

                if(highway_type in self.HIGHWAY_SPEED_LIMITS):
                    speed = self.HIGHWAY_SPEED_LIMITS[highway_type]
                    data['maxspeed'] = speed

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

            if(type(data['osmid']) != list):
                way_ids = [data['osmid']]
            else:
                way_ids = data['osmid']

            for way in way_ids:
                if(way not in way2nodes.keys()):
                    way2nodes[way] = []
                    way2nodes_pair[way] = []
                    way_lookup[way] = data
                    way_segment_lengths[way] = []
                way2nodes[way].extend([u,v])                    # add all nodes associated to a way
                way2nodes_pair[way].append([u,v])               # add pair of nodes belonging to way id
                way_segment_lengths[way].append(data['length']) # collect way lengths to sum up afterwards

            if(u not in segment_lengths.keys()):                # store each node-node direct segment length.
                segment_lengths[u] = {}                         # NOT DOING ANYTHING WITH IT FOR NOW
            segment_lengths[u][v] = data['length']

        # 1st FOR, build node id sequence belonging to way_id
        # 2nd FOR, sum segments lengths and add node id list to way lookup
        final_node_sequence = {}
        for way_id, values in way2nodes_pair.items(): # key: way_id, values: pairs of node ids
            relations = {}
            for pair in values:                       # build dict - key: node_pre - value: node post
                relations[pair[0]] = pair[1]
            keys = relations.keys()
            values_ = relations.values()              # if a key (node_pre) doesn't exist in values
            begin_key = list(keys - values_)          # it means it has only origin = way initial node

            if(len(values) > 1 and len(begin_key) == 1): # if NOT cyclic sequence?
                begin_key = begin_key[0]
                node_sequence = [begin_key]
                val = relations[begin_key]
                try:
                    while(val not in node_sequence):  # run through `relations` finding the node sequence pair by pair
                        node_sequence.append(val)
                        count += 1
                        begin_key = val
                        val = relations[begin_key]
                except Exception as e:                # until a pair is not found in the dict anymore = exception
                    e                                 # do nothing in exception
                final_node_sequence[way_id] = node_sequence # and store node "ordered" list as a Way metadata
            else:
                final_node_sequence[way_id] = list(keys)[0] + list(values_)[0] # if way has only 1 node, store it as it is

        for key, value in way_lookup.items():
            way_lookup[key]['length'] = np.sum(way_segment_lengths[key])
            way_lookup[key]['node_sequence'] = final_node_sequence[key]

        # build dict: key1: node1, key2: node2, value: way_id between ALL pair of nodes id IN way
        nodes2way = {}
        for key, values in way2nodes.items():
            for pair in combinations(values,2):
                if(pair[0] not in nodes2way.keys()):
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
        if(type(node_id_list) == int):
            return self.segment_lookup_[node_id_list[i]][node_id_list[i+1]]
        else:
            ways_id = []
            i = 0
            while i < len(node_id_list) - 1:
                ways_id.append(self.segment_lookup_[node_id_list[i]][node_id_list[i+1]])
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
        if(type(way_id_list) == int):
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
        if(type(node_id_list) == int):
            return self.node_lookup_[node_id_list]
        else:
            nodes_lookup = []
            for node in node_id_list:
                nodes_lookup.append(self.node_lookup_[node])
            return nodes_lookup

    @staticmethod
    def AMLD_local_lookups(place, network_type='drive_service'):
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
        with open('data/AMLD_lookups.pickle', 'rb') as f:
            node_lookup_, segment_lookup_, way_lookup_ = pickle.load(f)
        ra.node_lookup_ = node_lookup_
        ra.segment_lookup_ = segment_lookup_
        ra.way_lookup_ = way_lookup_
        return ra
