import networkx as nx
import random
from base_player import BasePlayer
from settings import *

class Player(BasePlayer):
    """
    You will implement this class for the competition. DO NOT change the class
    name or the base class.
    """

    # You can set up static state here
    has_built_station = False

    def __init__(self, state):
        """
        Initializes your Player. You can set up persistent state, do analysis
        on the input graph, engage in whatever pre-computation you need. This
        function must take less than Settings.INIT_TIMEOUT seconds.
        --- Parameters ---
        state : State
            The initial state of the game. See state.py for more information.
        """

        return

    # Checks if we can use a given path
    def path_is_valid(self, state, path):
        graph = state.get_graph()
        for i in range(0, len(path) - 1):
            if graph.edge[path[i]][path[i + 1]]['in_use']:
                return False
        return True

    # n is the numberr of nodes to select
    # k is the weighting of the the number of edges
    def select_first_station(self, graph, n=100, k=1):
        # sample = random.sample(xrange(100),n)#nx.number_of_nodes(graph)), n)
        nodes = graph.nodes()
        # sample_nodes = [nodes[i] for i in sample]
        sample_nodes = random.sample(nodes, n)
        node_weights = []
        for node in sample_nodes:
            distances =  nx.shortest_path_length(graph, source=node).values()
            ave_dist = sum(distances)/float(len(distances)) if len(distances)>0 else 9999999999999999999
            node_weights.append((ave_dist,node))
        return min(node_weights)[1]

    def score_orders(self, state, order):
        pass

    def step(self, state):
        """
        Determine actions based on the current state of the city. Called every
        time step. This function must take less than Settings.STEP_TIMEOUT
        seconds.
        --- Parameters ---
        state : State
            The state of the game. See state.py for more information.
        --- Returns ---
        commands : dict list
            Each command should be generated via self.send_command or
            self.build_command. The commands are evaluated in order.
        """

        # We have implemented a naive bot for you that builds a single station
        # and tries to find the shortest path from it to first pending order.
        # We recommend making it a bit smarter ;-)

        graph = state.get_graph()
        station = self.select_first_station(graph)#graph.nodes()[0]

        commands = []
        if not self.has_built_station:
            commands.append(self.build_command(station))
            self.has_built_station = True

        pending_orders = state.get_pending_orders()
        if len(pending_orders) != 0:
            order = random.choice(pending_orders)
            path = nx.shortest_path(graph, station, order.get_node())
            if self.path_is_valid(state, path):
                commands.append(self.send_command(order, path))

        return commands
