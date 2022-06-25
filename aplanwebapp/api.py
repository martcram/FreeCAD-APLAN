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

__title__ = "FreeCAD APLAN Flask web app API"
__author__ = "Martijn Cramer"
__url__ = "https://www.freecadweb.org"


from aplantools import aplanutils
try:
    import requests
    import typing
except ImportError as ie:
    aplanutils.missingPythonModule(str(ie.name or ""))


def clearCacheConnectionGraph() -> None:
    requests.post("http://0.0.0.0:8080/aplan/connection_graph/clear_cache")


def getConnectionGraph() -> typing.Dict:
    r = requests.get(
        "http://0.0.0.0:8080/aplan/connection_graph/json")
    return r.json()


def getConnectionGraphEdges() -> typing.Set[typing.Tuple]:
    connectionGraph: typing.Dict = getConnectionGraph()
    if connectionGraph:
        return {tuple(sorted([link["source"], link["target"]])) for link in getConnectionGraph()["links"]}
    else:
        return set()


def getSelectedConnections() -> typing.Dict:
    r = requests.get(
        "http://0.0.0.0:8080/aplan/connection_graph/selected_connections")
    return r.json()


def toggleAnimations(enable: bool) -> None:
    requests.post(
        "http://0.0.0.0:8080/aplan/connection_graph/animations?enable={}".format(str(enable)))
