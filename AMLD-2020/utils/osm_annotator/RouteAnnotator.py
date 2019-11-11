import osmnx as ox
import numpy as np
import networkx as nx

from itertools import combinations

class RouteAnnotator():

    # TODO add different forms of network retrieval from OSMNx
    def __init__(self, place, network_type):

        self.segment_lookup_ = None
        self.way_lookup_ = None
        self.G = None

        self.HIGHWAY_SPEED_LIMITS ={   # copied from https://github.com/Project-OSRM/osrm-backend/blob/master/profiles/car.lua
            'motorway':90,
            'motorway_link':45,
            'trunk':85,
            'trunk_link':40,
            'primary':65,
            'primary_link':30,
            'secondary':55,
            'secondary_link':25,
            'tertiary':40,
            'tertiary_link':20,
            'unclassified':25,
            'residential':25,
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

        self.G = ox.graph_from_place(place, network_type=network_type, simplify=False)
        self.add_speeds()
        self.build_lookups()

    def add_speeds(self):

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

    def build_lookups(self):
        # build segment lookup
        segment_lookup = {}
        way2nodes = {}
        way_lookup = {}

        # build segment lookup
        for u, v, k, data in self.G.edges(data=True, keys=True):

            if(type(data['osmid']) != list):
                way_ids = [data['osmid']]
            else:
                way_ids = data['osmid']

            for way in way_ids:
                if(way not in way2nodes.keys()):
                    way2nodes[way] = []
                    way_lookup[way] = data
                way2nodes[way].extend([u,v])

        nodes2way = {}
        for key, values in way2nodes.items():
            for pair in combinations(values,2):
                if(pair[0] not in nodes2way.keys()):
                    nodes2way[pair[0]] = {}
                nodes2way[pair[0]][pair[1]] = key

        self.segment_lookup_ = nodes2way
        self.way_lookup_ = way_lookup

    def segment_lookup(self, node_id_list):
        ways_id = []
        i = 0
        while i < len(node_id_list) - 1:
            ways_id.append(self.segment_lookup_[node_id_list[i]][node_id_list[i+1]])
            i += 1
        return ways_id

    def way_lookup(self, way_id_list):
        ways_lookup = []
        for way in ways_id:
            ways_lookup.append(self.way_lookup_[way])
        return ways_lookup
        
