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

__title__ = "FreeCAD APLAN geometrical constraints object"
__author__ = "Martijn Cramer"
__url__ = "https://www.freecadweb.org"

# @package geom_constraints
#  \ingroup APLAN
#  \brief FreeCAD APLAN geometrical constraints object

import FreeCAD
if FreeCAD.GuiUp:
    from aplanviewprovider.view_geom_constraints import VPGeomConstraints
from . import base_aplanpythonobject
from aplantools import aplanutils
from aplansolvers.aplan_obstruction_detectors import base_obstruction_detector as base
try:
    import typing
except ImportError as ie:
    print("Missing dependency! Please install the following Python module: {}".format(str(ie.name or "")))


def create(doc, analysis, motionDirection: base.IMotionDirection, constraints: typing.Set[typing.Tuple[str, str]], name="GeomConstraints"):
    obj = doc.addObject(GeomConstraints.BaseType, name)
    aplanutils.getConstraintGroup(analysis).addObject(obj)
    GeomConstraints(obj, analysis, motionDirection, constraints)
    if FreeCAD.GuiUp:
        VPGeomConstraints(obj.ViewObject)
    return obj


class GeomConstraints(base_aplanpythonobject.BaseAplanPythonObject):
    BaseType = "Aplan::GeomConstraintsPython"

    def __init__(self, obj, analysis, motionDirection: base.IMotionDirection, constraints: typing.Set[typing.Tuple[str, str]]) -> None:
        super(GeomConstraints, self).__init__(obj)
