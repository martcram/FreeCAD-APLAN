from enum import IntEnum
from halp.directed_hypergraph import DirectedHypergraph
import itertools
import matplotlib.pyplot as plt
import networkx as nx
import math
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


class Subassembly:
    def __init__(self, components=[]):
        self.components = sorted(list(set(components)))
    
    def get_components(self):
        return self.components

    def add_component(self, component):
        if component not in self.components:
            self.components.append(component)
            self.components.sort()

    def remove_component(self, component):
        self.components.remove(component)

    def __eq__(self, other):
        return self.components == other.components

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(tuple(self.components))


class AndOrGraph(DirectedHypergraph):
    def __init__(self):
        super().__init__()

    def add_edge(self, parent_subasm, child_subasms):
        self.add_hyperedge([parent_subasm], set(child_subasms))
    
    def add_edges(self, edges):
        for edge in edges:
            self.add_edge(edge[0], edge[1])

    def generate(self, connection_graph, obstruction_graphs=[]):
        nodes = connection_graph.nodes
        geometrical_constraints = self.__get_geometrical_constraints(nodes, obstruction_graphs)
        
        subasm_sizes = {}
        subasm_sizes[1] = [[node] for node in nodes]
        subasm_sizes[2] = [list(edge) for edge in connection_graph.edges if self.__check_geometrical_feasibility(edge, geometrical_constraints)]
        subasm_sizes[len(nodes)] = [sorted(nodes)]

        # find all feasible (sub)assemblies by gradually increasing the subassembly size
        neighbors = {node: self.__get_adjoining_components([node], connection_graph) for node in nodes}
        for length in range(3, len(nodes)):
            subasms = []
            for subasm in subasm_sizes[length-1]:
                subasm_neighbors = self.__get_adjoining_components(subasm, connection_graph)
                new_subasms = [sorted(subasm + [neighbor]) for neighbor in subasm_neighbors]
                subasms += filter(lambda subasm: (subasm not in subasms) and (self.__check_geometrical_feasibility(subasm, geometrical_constraints)), new_subasms)
            subasm_sizes[length] = subasms

        # create triplets and compose AND-OR graph's edges
        for triplet3_len in range(3, len(nodes)+1)[::-1]:
            for triplet1_len in range(math.ceil(triplet3_len/2) , triplet3_len)[::-1]:
                triplet2_len = triplet3_len - triplet1_len
                triplets = itertools.product(subasm_sizes[triplet1_len], subasm_sizes[triplet2_len], subasm_sizes[triplet3_len])
                for triplet in triplets:
                    if self.__validate_triplet(triplet):
                        parent_subasm = Subassembly(list(triplet[2]))
                        child_subasm = [Subassembly(subasm) for subasm in triplet[0:2]]
                        self.add_edge(parent_subasm, child_subasm)
        
        # add hyperedges of 2-component subassemblies
        for subasm in subasm_sizes[2]:
            self.add_edge(Subassembly(subasm), [Subassembly([subasm[0]]), Subassembly([subasm[1]])])

    def __get_adjoining_components(self, subasm, connection_graph):
        adjoining_components = []
        for component in subasm:
            adjoining_components += list(connection_graph.neighbors(component))
        adjoining_components = filter(lambda comp: comp not in subasm, list(set(adjoining_components)))
        return list(adjoining_components)

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
                if not obstructing_subasm:
                    return True
                elif target not in subasm and (set(obstructing_subasm).issubset(set(subasm))):
                    return False
        return True

    def __check_technical_feasibility(self, subasm, technical_constraints):
        for target, obstructing_subasms in technical_constraints.items():
            for obstructing_subasm in obstructing_subasms:
                if target not in subasm and (set(obstructing_subasm).issubset(set(subasm))):
                    return False
        return True

    def __validate_triplet(self, triplet):
        intersection = set(triplet[0]).intersection(set(triplet[1]))
        union = set(triplet[0]).union(set(triplet[1]))
        return intersection == set() and sorted(union) == sorted(triplet[2])