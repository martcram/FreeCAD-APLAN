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


from aplantools import aplanutils
try:
    import json
    import networkx as nx
    import typing
except ImportError as ie:
    aplanutils.missingPythonModule(str(ie.name or ""))


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
            aplanutils.displayAplanError(
                "Connection graph cannot be exported to '{}'.".format(fileLoc), repr(e))

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
            aplanutils.displayAplanError(
                "Connection graph cannot be imported from '{}'.".format(fileLoc), repr(e))
        return self

    def createFromJSON(self, jsonData: typing.Dict) -> ConnectionGraph:
        try:
            edges: typing.List[typing.Tuple] = [(link["source"], link["target"])
                                                for link in jsonData["links"]]
            self.clear()
            self.add_edges_from(edges)
        except Exception as e:
            aplanutils.displayAplanError(
                "Connection graph cannot be created from JSON data", repr(e))
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
            aplanutils.displayAplanError(
                "Obstruction graph cannot be exported to '{}'.".format(fileLoc), repr(e))

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
            aplanutils.displayAplanError(
                "Obstruction graph cannot be imported from '{}'.".format(fileLoc), repr(e))
        return self

    def createFromJSON(self, jsonData: typing.Dict) -> ObstructionGraph:
        try:
            edges: typing.List[typing.Tuple] = [(link["source"], link["target"])
                                                for link in jsonData["links"]]
            self.clear()
            self.add_edges_from(edges)
        except Exception as e:
            aplanutils.displayAplanError(
                "Obstruction graph cannot be created from JSON data", repr(e))
        return self
