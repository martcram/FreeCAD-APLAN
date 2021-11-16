# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2020 Bernd Hahnebach <bernd@bimstatik.org>              *
# *   Copyright (c) 2021 Martijn Cramer <martijn.cramer@outlook.com>        *
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

## @package topo_constraints
#  \ingroup APLAN
#  \brief FreeCAD APLAN topological constraints object

import FreeCAD

from . import base_aplanpythonobject
from aplanviewprovider.view_topo_constraints import ViewProviderTopoConstraints


def create(doc, name="TopoConstraints"):
    obj = doc.addObject(TopoConstraints.BaseType, name)
    TopoConstraints(obj)
    if FreeCAD.GuiUp:
        ViewProviderTopoConstraints(obj.ViewObject)
    return obj


class TopoConstraints(base_aplanpythonobject.BaseAplanPythonObject):
    
    Type = "App::DocumentObject"

    def __init__(self, obj):
        super(TopoConstraints, self).__init__(obj)
