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

__title__ = "FreeCAD APLAN part filter object"
__author__ = "Martijn Cramer"
__url__ = "https://www.freecadweb.org"

# @package part_filter
#  \ingroup APLAN
#  \brief FreeCAD APLAN part filter object

import FreeCAD
if FreeCAD.GuiUp:
    from aplanviewprovider.view_part_filter import ViewProviderPartFilter
from . import base_aplanpythonobject
from aplantools import aplanutils


def create(doc, name: str = "PartFilter"):
    return aplanutils.createObject(doc, name, PartFilter, ViewProviderPartFilter)


class PartFilter(base_aplanpythonobject.BaseAplanPythonObject):
    BaseType = "Aplan::PartFilterPython"

    def __init__(self, obj):
        super(PartFilter, self).__init__(obj)
