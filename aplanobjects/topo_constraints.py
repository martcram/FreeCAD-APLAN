# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2020 Bernd Hahnebach <bernd@bimstatik.org>              *
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

__title__ = "FreeCAD APLAN topological constraints object"
__author__ = "Martijn Cramer, Bernd Hahnebach"
__url__ = "https://www.freecadweb.org"

# @package topo_constraints
#  \ingroup APLAN
#  \brief FreeCAD APLAN topological constraints object

import FreeCAD
if FreeCAD.GuiUp:
    from aplanviewprovider.view_topo_constraints import VPTopoConstraints
from . import base_aplanpythonobject
from aplanobjects import graphs
from aplantools import aplanutils
try:
    import typing
except ImportError as ie:
    print("Missing dependency! Please install the following Python module: {}".format(str(ie.name or "")))


def create(doc, analysis, constraints: typing.Set[typing.Tuple[str, str]], name="TopoConstraints"):
    obj = doc.addObject(TopoConstraints.BaseType, name)
    aplanutils.getConstraintGroup(analysis).addObject(obj)
    TopoConstraints(obj, analysis, constraints)
    if FreeCAD.GuiUp:
        VPTopoConstraints(obj.ViewObject)
    return obj


class TopoConstraints(base_aplanpythonobject.BaseAplanPythonObject):
    BaseType = "Aplan::TopoConstraintsPython"

    def __init__(self, obj, analysis, constraints: typing.Set[typing.Tuple[str, str]]) -> None:
        super(TopoConstraints, self).__init__(obj)
        if hasattr(obj, "FileLocation"):
            obj.FileLocation = "{}/{}.json".format(analysis.WorkingDir, obj.Label)

            conGraph: graphs.ConnectionGraph = graphs.ConnectionGraph()
            if len(constraints) == 0:
                conGraph.add_nodes_from([component.Label for component in analysis.Components])
            else:
                conGraph.add_edges_from(constraints)
                for component in analysis.Components:
                    if component.Label not in conGraph.nodes:
                        conGraph.add_node(component.Label)
            
            conGraph.exportToFile(obj.FileLocation)
