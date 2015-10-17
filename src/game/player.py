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
    stations = []

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

    def remove_in_use(self, graph):
        for edge in graph.edges():
            if graph.edge[edge[0]][edge[1]]['in_use']:
                graph.remove_edge(edge[0], edge[1])

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
        
        graph = state.get_graph()
        commands = []
        # naive build station
        if not self.has_built_station:
            station = graph.nodes()[0]
            commands.append(self.build_command(station))
            self.has_built_station = True
            self.stations.append(station)

        # baseline job-picking
        pending_orders = state.get_pending_orders()
        if len(pending_orders) != 0:
            # make copy of graph
            # remove all edges in use
            # shortest path from each station to job
            tempGraph = graph.copy()
            self.remove_in_use(tempGraph)

            bestMoney = 0
            bestStation = None
            bestOrder = None
            bestPath = None
            for station in self.stations:
                for order in pending_orders:
                    try:
                        p=nx.shortest_path(tempGraph, source=station, target=order.node)
                    except nx.NetworkXException:
                        pass
                    else:
                        expectedMoney = order.money - DECAY_FACTOR*len(p)
                        if expectedMoney > bestMoney:
                            bestMoney = expectedMoney
                            bestStation = station
                            bestOrder = order
                            bestPath = p
            if bestMoney > 0:
                commands.append(self.send_command(bestOrder, bestPath))

        return commands
