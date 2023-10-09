from __future__ import annotations

# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2022 Martijn Cramer <martijn.cramer@outlook.com>        *
# *                                                                         *
# *   This file is part of the FreeCAD CAx development system.              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

__title__ = "FreeCAD APLAN's graph classes"
__author__ = "Martijn Cramer"
__url__ = "https://www.freecadweb.org"

try:
    from collections import defaultdict
    import graphviz
    import json
    import networkx as nx
    import pickle
    import typing
    import uuid
except ImportError as ie:
    print("Missing dependency! Please install the following Python module: {}".format(str(ie.name or "")))


class ConnectionGraph(nx.Graph):
    def __init__(self) -> None:
        super().__init__()

    def exportToFile(self, fileLoc: str) -> None:
        try:
            jsonData: typing.Dict = {}
            jsonData["nodes"] = [{"name": node} for node in self.nodes()]
            jsonData["links"] = [{"source": str(edge[0]),
                                  "target": str(edge[1])} for edge in self.edges()]
            with open(fileLoc, 'w') as file:
                json.dump(jsonData, file)
        except Exception as e:
            print("Connection graph cannot be exported to '{}': {}.".format(fileLoc, repr(e)))

    def importFromFile(self, fileLoc: str) -> ConnectionGraph:
        try:
            jsonData: typing.Dict = {}
            with open(fileLoc, 'r') as file:
                jsonData = json.load(file)
            edges: typing.List[typing.Tuple] = [(link["source"], link["target"])
                                                for link in jsonData["links"]]
            self.clear()
            self.add_edges_from(edges)
        except Exception as e:
            print("Connection graph cannot be imported to '{}': {}.".format(fileLoc, repr(e)))
        return self

    def createFromJSON(self, jsonData: typing.Dict) -> ConnectionGraph:
        try:
            edges: typing.List[typing.Tuple] = [(link["source"], link["target"])
                                                for link in jsonData["links"]]
            self.clear()
            self.add_edges_from(edges)
        except Exception as e:
            print("Connection graph cannot be created from JSON data: {}".format(repr(e)))
        return self


class ObstructionGraph(nx.DiGraph):
    def __init__(self) -> None:
        super().__init__()

    def exportToFile(self, fileLoc: str) -> None:
        try:
            jsonData: typing.Dict = {}
            jsonData["nodes"] = [{"name": node} for node in self.nodes()]
            jsonData["links"] = [{"source": str(edge[0]),
                                  "target": str(edge[1])} for edge in self.edges()]
            with open(fileLoc, 'w') as file:
                json.dump(jsonData, file)
        except Exception as e:
            print("Obstruction graph cannot be exported to '{}': {}.".format(fileLoc, repr(e)))

    def importFromFile(self, fileLoc: str) -> ObstructionGraph:
        try:
            jsonData: typing.Dict = {}
            with open(fileLoc, 'r') as file:
                jsonData = json.load(file)
            edges: typing.List[typing.Tuple] = [(link["source"], link["target"])
                                                for link in jsonData["links"]]
            self.clear()
            self.add_edges_from(edges)
        except Exception as e:
            print("Obstruction graph cannot be imported to '{}': {}.".format(fileLoc, repr(e)))
        return self

    def createFromJSON(self, jsonData: typing.Dict) -> ObstructionGraph:
        try:
            edges: typing.List[typing.Tuple] = [(link["source"], link["target"])
                                                for link in jsonData["links"]]
            self.clear()
            self.add_edges_from(edges)
        except Exception as e:
            print("Obstruction graph cannot be created from JSON data: {}".format(repr(e)))
        return self


class AndOrGraph:
    def __init__(self) -> None:
        self.nodes = set()
        self.edges = set()
        self.incoming_edges = defaultdict(set)
        self.outgoing_edges = defaultdict(set)
        self.parent_nodes = defaultdict(set)
        self.child_nodes = defaultdict(set)

    def add_node(self, node: Node) -> None:
        self.nodes.add(node)

    def add_nodes_from(self, nodes: typing.Iterable[Node]) -> None:
        self.nodes.update(set(nodes))

    def remove_node(self, node: Node) -> None:
        self.nodes.remove(node)

        for parent_node in self.parent_nodes[node]:
            self.child_nodes[parent_node].remove(node)
        if node in self.parent_nodes.keys():
            self.parent_nodes.pop(node)

        for child_node in self.child_nodes[node]:
            self.parent_nodes[child_node].remove(node)
        if node in self.child_nodes.keys():
            self.child_nodes.pop(node)

        for edge in self.incoming_edges[node]:
            self.edges.remove(edge)
            for child_node in edge.child_nodes:
                if child_node is not node:
                    self.incoming_edges[child_node].remove(edge)
            self.outgoing_edges[edge.parent_node].remove(edge)
        if node in self.incoming_edges.keys():
            self.incoming_edges.pop(node)

        for edge in self.outgoing_edges[node]:
            self.edges.remove(edge)
            for child_node in edge.child_nodes:
                self.incoming_edges[child_node].remove(edge)
        if node in self.outgoing_edges.keys():
            self.outgoing_edges.pop(node)

    def get_node(self, elements):
        elements.sort()
        for node in self.nodes:
            if node.elements == elements:
                return node

    def add_edge(self, edge):
        self.edges.add(edge)
        for child_node in edge.child_nodes:
            self.incoming_edges[child_node].add(edge)
            self.outgoing_edges[edge.parent_node].add(edge)
            self.parent_nodes[child_node].add(edge.parent_node)
            self.child_nodes[edge.parent_node].add(child_node)

    def add_edges_from(self, edges):
        self.edges.update(set(edges))
        for edge in edges:
            for child_node in edge.child_nodes:
                self.incoming_edges[child_node].add(edge)
                self.outgoing_edges[edge.parent_node].add(edge)
                self.parent_nodes[child_node].add(edge.parent_node)
                self.child_nodes[edge.parent_node].add(child_node)

    def remove_edge(self, edge):
        self.edges.remove(edge)
        self.outgoing_edges[edge.parent_node].remove(edge)
        for child_node in edge.child_nodes:
            self.incoming_edges[child_node].remove(edge)

    def plot(self, file_loc, **kwargs):
        dot = graphviz.Digraph()

        for node in self.nodes:
            if node.type == 'end':
                dot.node(str(node.guid), label=f'{node.name}: {str(node.cost)}',
                         shape='rect', style='filled', fillcolor='gold1')
            else:
                dot.node(str(node.guid),
                         label=f'{node.name}: {str(node.cost)}', shape='rect')

            colorBool = False
            for edge in self.outgoing_edges[node]:
                colorBool = not colorBool
                if edge in self.edges:
                    for child in edge.child_nodes:
                        if child in self.nodes:
                            if colorBool:
                                if edge.agent != "":
                                    dot.edge(str(node.guid), str(
                                        child.guid), color='blue', label=f'{edge.agent}: {str(edge.cost[edge.agent])}')
                                else:
                                    dot.edge(str(node.guid), str(
                                        child.guid), color='blue')
                            else:
                                if edge.agent != "":
                                    dot.edge(str(node.guid), str(
                                        child.guid), color='red', label=f'{edge.agent}: {str(edge.cost[edge.agent])}')
                                else:
                                    dot.edge(str(node.guid), str(
                                        child.guid), color='red')

        dot.format = 'png'
        dot.attr(dpi='200')
        dot.render(f'{file_loc}/AND-OR_graph{kwargs.get("index", "")}', view=False)

    def save(self, file_loc):
        with open(f'{file_loc}/AND-OR_graph.pickle', "wb") as output_file:
            pickle.dump(self.__dict__, output_file)

    def load(self, file_loc):
        name = self.name 
        with open(file_loc, "rb") as input_file:
            self.__dict__.update(pickle.load(input_file))
        self.name = name


class Node:
    def __init__(self, elements):
        self.guid = uuid.uuid4()
        self.name = f'[{", ".join(elements)}]'
        self.elements = elements


class AndEdge:
    def __init__(self, parent_node, child_nodes):
        self.parent_node = parent_node
        self.child_nodes = child_nodes