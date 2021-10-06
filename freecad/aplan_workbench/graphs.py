from enum import IntEnum
from halp.directed_hypergraph import DirectedHypergraph
import itertools
import matplotlib.pyplot as plt
import networkx as nx
import os


class ConnectionGraph(nx.Graph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if 'name' not in self.graph:
            self.name = kwargs.get('name', 'undefined')
        else:
            self.name = self.graph['name']

    def save(self, file_loc, fig_size=(10, 10), dpi=200):
        if not os.path.exists(file_loc):
            os.mkdir(file_loc)

        fig = plt.figure(figsize=fig_size, dpi=dpi)
        pos = nx.nx_agraph.graphviz_layout(self, prog='dot')
        nx.draw(self, pos, with_labels=True, arrows=False, node_size=3000, node_color='lightskyblue')

        print(f'Saving connection graph of {self.name} to: {file_loc}\n')
        fig.savefig(f'{file_loc}/{self.name}_connection_graph.png', dpi=dpi)
        nx.nx_agraph.write_dot(self, f'{file_loc}/{self.name}_connection_graph.dot')
    
    def load(self, file_path):
        G = nx.Graph(nx.nx_agraph.read_dot(file_path))
        self.__dict__.update(G.__dict__)


class ObstructionGraph(nx.DiGraph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if 'name' not in self.graph:
            self.name = kwargs.get('name', 'undefined')
        else:
            self.name = self.graph['name']

        if 'motion_direction' not in self.graph:
            self.motion_direction = kwargs.get('motion_direction', MotionDirection.UNDEF)
        else:
            if type(self.graph['motion_direction']) == str:
                self.motion_direction = MotionDirection[self.graph['motion_direction'].split('.')[1]]
            else:
                self.motion_direction = self.graph['motion_direction']

    def reverse(self):
        rev_obstruct_graph = ObstructionGraph(name=self.name, motion_direction=MotionDirection(-self.motion_direction))
        rev_obstruct_graph.add_nodes_from(self.nodes())
        rev_obstruct_graph.add_edges_from({edge[::-1] for edge in self.edges()})
        
        return rev_obstruct_graph

    def save(self, file_loc, fig_size=(10, 10), dpi=200):
        if not os.path.exists(file_loc):
            os.mkdir(file_loc)

        fig = plt.figure(figsize=fig_size, dpi=dpi)
        pos = nx.nx_agraph.graphviz_layout(self, prog='dot')
        nx.draw(self, pos, with_labels=True, arrows=True, node_size=3000, node_color='lightskyblue')

        print(f'Saving obstruction graph of {self.name} in {self.motion_direction.name} direction to: {file_loc}\n')
        fig.savefig(f'{file_loc}/{self.name}_{self.motion_direction.name}_obstruction_graph.png', dpi=dpi)
        nx.nx_agraph.write_dot(self, f'{file_loc}/{self.name}_{self.motion_direction.name}_obstruction_graph.dot')

    def load(self, file_path):
        G = nx.DiGraph(nx.nx_agraph.read_dot(file_path))
        self.__dict__.update(G.__dict__)


class MotionDirection(IntEnum):
    UNDEF = 0
    NEG_X = -1
    POS_X = 1
    NEG_Y = -2
    POS_Y = 2
    NEG_Z = -3
    POS_Z = 3


class AndOrGraph(DirectedHypergraph):
    def __init__(self):
        super().__init__()

    def add_edge(self, parent_subasm, child_subasms):
        self.add_hyperedge([parent_subasm], set(child_subasms))
    
    def add_edges(self, edges):
        for edge in edges:
            self.add_edge(edge[0], edge[1])

    def generate(self, connection_graph, obstruction_graphs):
        nodes = connection_graph.nodes
        geometrical_constraints = self.__get_geometrical_constraints(nodes, obstruction_graphs)

    def __get_geometrical_constraints(self, nodes, obstruction_graphs):
        geometrical_constraints = {}
        
        for target in nodes:
            target_successors = [obstruction_graph.successors(target) for obstruction_graph in obstruction_graphs]
            obstructing_subasms = itertools.product(*target_successors)

            obstructing_subasms_wo_dupl = []
            for obstructing_subasm in obstructing_subasms:
                obstructing_subasms_temp = sorted(list(set(obstructing_subasm))) # remove duplicate assembly components
                if obstructing_subasms_temp not in obstructing_subasms_wo_dupl: # prevent duplicates from being added
                    obstructing_subasms_wo_dupl.append(obstructing_subasms_temp)

            if obstructing_subasms_wo_dupl:
                geometrical_constraints[target] = obstructing_subasms_wo_dupl

        return geometrical_constraints

    def __check_geometrical_feasibility(self, subasm, geometrical_constraints):
        for target, obstructing_subasms in geometrical_constraints.items():
            for obstructing_subasm in obstructing_subasms:
                if target not in subasm and (set(obstructing_subasm).issubset(set(subasm))):
                    return False
        return True
