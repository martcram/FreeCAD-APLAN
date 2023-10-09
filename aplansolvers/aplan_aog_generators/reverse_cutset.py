# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2023 Martijn Cramer <martijn.cramer@outlook.com>        *
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

__title__ = ""
__author__ = "Martijn Cramer"
__url__ = "https://www.freecadweb.org"

import aplansolvers.aplan_aog_generators.base_aog_generator as base
import aplanobjects.graphs as graphs

import itertools
import math
import numpy as np
import typing


class ReverseCutset(base.IAndOrGraphGenerator):
    def __init__(self, obj, components: typing.Set[str], constraints: typing.Dict) -> None:
        super().__init__(obj, components, constraints)

    def addProperties(self, obj) -> None:
        if hasattr(obj, "Type"):
            obj.Type = self.__class__.__name__

    def generate(self) -> graphs.AndOrGraph:
        nodes = self._components
        nof_nodes = len(nodes)
        
        sublength_dict = {1: [[node] for node in nodes], 2: [list(edge) for edge in self._topoConstraints.edges if self.__checkGeometricalFeasibility(edge)], nof_nodes: [sorted(nodes)]}
        neighbor_dict = {node: list(self._topoConstraints.neighbors(node)) for node in nodes}

        for length in range(3, nof_nodes):
            subassemblies = []
            for subassembly in sublength_dict[length-1]:
                neighbors = np.unique([neighbor for node in subassembly for neighbor in neighbor_dict[node] if neighbor not in subassembly])
                subassemblies_temp = [sorted(list(itertools.chain.from_iterable([[item] if type(item) != list else item for item in prod]))) for prod in itertools.product([subassembly], neighbors)]
                subassemblies += [subassembly for subassembly in subassemblies_temp if subassembly not in subassemblies and self.__checkGeometricalFeasibility(subassembly)]
            sublength_dict[length] = subassemblies
        subassemblies = sorted(list(itertools.chain.from_iterable(sublength_dict.values())), key=len)[::-1]

        cutsets = []
        append = cutsets.append
        for triplet3_len in range(3,nof_nodes+1)[::-1]:
            for triplet1_len in range(math.ceil(triplet3_len/2),triplet3_len)[::-1]:
                for triplet in list(itertools.product(sublength_dict[triplet1_len],sublength_dict[triplet3_len-triplet1_len],sublength_dict[triplet3_len])):
                    if sorted(list(itertools.chain.from_iterable(triplet[0:2]))) == triplet[2] and list(set(triplet[0])&set(triplet[1])) == []: append([subassemblies.index(triplet[2]), sorted(triplet[0:2])])
        cutsets += [[subassemblies.index(two_subassembly), [[two_subassembly[0]], [two_subassembly[1]]]] for two_subassembly in sublength_dict[2]]

        cutset_dict = {key: list(itertools.chain.from_iterable([group[1:] for group in list(groups)])) for key, groups in itertools.groupby(sorted(cutsets), lambda x: x[0])}

        oa_graph = graphs.AndOrGraph()
        nodes = {graphs.Node(elements=sorted(subassembly)) for subassembly in subassemblies}
        oa_graph.add_nodes_from(nodes)
        
        edges = set()
        for key, cutsets in cutset_dict.items():
            parent_node = oa_graph.get_node(subassemblies[key])
            for cutset in cutsets:
                child_nodes = [oa_graph.get_node(cut) for cut in cutset]
                edges.add(graphs.AndEdge(parent_node, child_nodes))
        oa_graph.add_edges_from(edges)

        return oa_graph