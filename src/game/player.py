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

#--------------------------------------------------------
#HELPER FUNCTIONS
#--------------------------------------------------------

    # Checks if we can use a given path
    def path_is_valid(self, state, path):
        graph = state.get_graph()
        for i in range(0, len(path) - 1):
            if graph.edge[path[i]][path[i + 1]]['in_use']:
                return False
        return True

    # Given a graph, returns a graph with all edges in use removed
    def remove_in_use(self, graph):
        for edge in graph.edges():
            if graph.edge[edge[0]][edge[1]]['in_use']:
                graph.remove_edge(edge[0], edge[1])

    # returns expected reward of order given distance
    def expected_reward(self, order, distance):
        return order.money - DECAY_FACTOR*distance

#--------------------------------------------------------

    # n is the numberr of nodes to select
    # k is the weighting of the the number of edges
    def select_first_station(self, graph, n=None, k=0.5):
        # sample = random.sample(xrange(100),n)#nx.number_of_nodes(graph)), n)
        nodes = graph.nodes()
        # sample_nodes = [nodes[i] for i in sample]
        sample_nodes = random.sample(nodes, n) if n!=None else nodes
        node_weights = []
        for node in sample_nodes:
            distances =  nx.shortest_path_length(graph, source=node).values()
            ave_dist = sum(distances)/float(len(distances)) if len(distances)>0 else 9999999999999999999
            degree = float(len(nx.neighbors(graph, node)))
            node_weights.append((ave_dist/(degree*k),node))
        return min(node_weights)[1]

    def score_commands(self, state, stations, paths):
        profit = 0
        money = state.money
        immediate = reward_from_new_widget_deliveries
        rate_profit = 1+newstations/currentstations
        c = 1/3.
        time_remaining = total_time - state.time
        profit = money + immediate*0.8 + rate_profit * time_remaining
        return profit

    def baseline_get(self, graph, pending_orders):
        bestMoney = 0
        bestStation = None
        bestOrder = None
        bestPath = None
        for station in self.stations:
            for order in pending_orders:
                try:
                    p=nx.shortest_path(graph, source=station, target=order.node)
                except nx.NetworkXException:
                    pass
                else:
                    expectedMoney = self.expected_reward(order, len(p))
                    if expectedMoney > bestMoney:
                        bestMoney = expectedMoney
                        bestStation = station
                        bestOrder = order
                        bestPath = p
        return (bestMoney,bestStation,bestOrder,bestPath)

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

        if not self.has_built_station:
            station = self.select_first_station(graph)
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

            (money,station,order,path) = self.baseline_get(tempGraph, pending_orders)
            if money > 0:
                commands.append(self.send_command(order, path))

        return commands
