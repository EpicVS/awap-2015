from collections import deque
import networkx as nx
import random
from base_player import BasePlayer
import game
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

    def station_cost(self):
        return STATION_COST*BUILD_FACTOR**(len(self.stations)-1)

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

    def make_random_command(self, state):
        pass

    def good_station(self, state):
        dist = [10000 for n in state.graph.nodes()]
        for station in self.stations:
            tree = nx.shortest_path(state.graph, source = station)
            for k, v in tree.items():
                dist[k-1] = min(dist[k-1],v)
        deg = [state.graph.degree(x+1) for x in xrange(len(d2n))]
        value = [x*dist[i] for i, x in enumerate(deg)]
        imax = -1
        vmax = 0
        for i, x in enumerate(deg):
            if x*dist[i] > vmax:
                vmax = x*dist[i]
                imax = i
        assert imax != -1
        return i+1

    #scoring function
    def score_commands(self, state, num_station, ordertups, verbose = False):
        order, path = zip(*ordertups)
        #!!!!!!!!!
        perstationcost = self.station_cost()
        money = perstationcost*num_station
        immediate = sum([self.expected_reward(order.money, len(path)) for order in orders])
        rate_profit = num_station/len(self.stations)*income
        time_remaining = GAME_LENGTH - state.time
        if verbose:
            print money
            print immediate*0.8
            print rate_profit*0.7*time_remaining
        return money + immediate * 0.8 + rate_profit * 0.7 * time_remaining

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

        '''
            generate list of candidate stationss
            *--generate list of orders sorted by time senstive reward
            take first x of those and generate subsets
            evalueate ricsons functions on each subset
            pick greatest.
        '''
        if len(pending_orders) != 0:
            tempGraph = graph.copy()
            self.remove_in_use(tempGraph)

            sorted_orders = sorted([(self.expected_reward(order, \
                min([nx.shortest_path_length(tempGraph,source=station,target=order.get_node())\
                for station in stations])), order) for order in pending_orders])[:10]

            #list of list of orders
            best_orders_lists=[]

            for i in range(10):
                shuffled_orders = random.shuffle(sorted_orders)
                tempGraph2 = tempGraph.copy()
                for order in shuffled_orders:
                    p=[0 for i in range(9999)]
                    for station in self.stations:
                        try:
                            temp_p = nx.shortest_path(graph, source=station, target=order.node)
                            if(len(temp_p)<len(p)):
                                p = temp_p
                        except nx.NetworkXException:
                            pass
                    if len(p) != 9999:
                        for (u, v) in game.path_to_edges(path):
                            G.edge[u][v]['in_use'] = True
                            G.edge[v][u]['in_use'] = True
                            self.remove_in_use(tempGraph2)
                            best_orders_lists.append((shuffled_orders[1],p))


            if len(best_orders_lists)>0:
                command_scores = []
                for commands in best_orders_lists:
                    numStations = 0 if random.random()>0.1 else 1
                    command_scores.append(self.score_commands(state,numStations, commands),commands, numStations)

                (best_score,best_command,numStations) = max(command_scores)

                if numStations>1:
                    commands.append(self.build_command(self.good_station(state)))
                commands.append(self.send_command(best_command[0],best_command[1]))


            # make copy of graph
            # remove all edges in use
            # shortest path from each station to job


            # (value,station,order,path) = self.baseline_get(tempGraph, pending_orders)
            # if value > 0:
                # commands.append(self.send_command(order, path))

        return commands
