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

import aplanobjects.graphs as graphs

import abc
import copy
import itertools
import networkx as nx
import numpy as np
import typing


class IAndOrGraphGenerator(metaclass=abc.ABCMeta):
    def __init__(self, obj, components: typing.Set[str], constraints: typing.Dict) -> None:
        obj.Proxy = self
        if not hasattr(obj, "Type"):
            obj.addProperty(
                "App::PropertyString",
                "Type",
                "AND/OR graph generator",
                "Type of AND/OR graph generator"
            )
            obj.setEditorMode("Type", 1)  # read-only

        self._components = components

        self._topoConstraints: graphs.ConnectionGraph = graphs.ConnectionGraph()
        if "topological" in constraints:
            self._topoConstraints = constraints["topological"]
        else:
            # create a strongly connected connection graph
            edges: typing.List[typing.Tuple[str, str]] = []
            for comp in self._components:
                temp: typing.Set[str] = copy.deepcopy(self._components)
                temp.remove(comp)
                edges += list(itertools.product([comp], temp))
            self._topoConstraints.add_edges_from(edges)

        self._geomConstraints: typing.List[graphs.ObstructionGraph] = constraints.get("geometrical", [graphs.ObstructionGraph()])
        
        self._blockingRules: typing.Dict[str, typing.List[typing.List[str]]] = {}
        if self._geomConstraints:
            self._blockingRules = self.__getBlockingRules(self._components, self._geomConstraints)

    def __checkTopologicalFeasibility(self, subassembly: typing.Iterable[str]) -> typing.Tuple[typing.Tuple[bool, str], bool]:
        succeeded: bool = False
        errorMsg: str = ""
        topoFeasible: bool = False

        excessComponents: typing.Set[str] = set(subassembly).difference(set(self._topoConstraints.nodes))
        if excessComponents:
            succeeded = False
            errorMsg = "[TOPO_CHECK]: The following component(s) is/are not part of the connection graph: {}".format(excessComponents)
        else:
            succeeded = True
            topoFeasible = nx.is_connected(self._topoConstraints.subgraph(subassembly))

        return ((succeeded, errorMsg), topoFeasible)

    def __checkGeometricalFeasibility(self, subassembly: typing.Iterable[str]) -> typing.Tuple[typing.Tuple[bool, str], bool]:
        succeeded: bool = False
        errorMsg: str = ""
        geomFeasible: bool = True

        for component, rules in self._blockingRules.items():
            for rule in rules:
                if (set(rule).issubset(set(subassembly)) and component not in subassembly):
                    geomFeasible = False
        succeeded = True

        return ((succeeded, errorMsg), geomFeasible)

    def __getBlockingRules(self, components: typing.Iterable[str], geomConstraints: typing.Iterable[graphs.ObstructionGraph]) -> typing.Dict[str, typing.List[typing.List[str]]]:
        blockingRulesTemp = {comp: [list(set(prod)) for prod in itertools.product(*[obstructionGraph.successors(comp) for obstructionGraph in geomConstraints])] for comp in components}
        return {component: list(np.unique(np.array(rule, dtype=object))) for component, rule in blockingRulesTemp.items() if rule != []}

    def __getstate__(self) -> None:
        return None

    def __setstate__(self, state) -> None:
        return None