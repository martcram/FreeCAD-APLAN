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

__title__ = "FreeCAD APLAN compound object"
__author__ = "Martijn Cramer"
__url__ = "https://www.freecadweb.org"

# @package compound
#  \ingroup APLAN
#  \brief FreeCAD APLAN compound object

from aplantools import aplanutils
try:
    from . import base_aplanpythonobject
    from aplantools import aplanutils
    from aplanviewprovider.view_compound import ViewProviderCompound
    import FreeCAD
    import typing
except ImportError as ie:
    aplanutils.missingPythonModule(str(ie.name or ""))


def create(doc, analysis, components: typing.List, name="Compound"):
    obj = FreeCAD.ActiveDocument.addObject(Compound.BaseType, name)
    obj.Links = components
    aplanutils.getCompoundGroup(analysis).addObject(obj)
    Compound(obj)
    if FreeCAD.GuiUp:
        ViewProviderCompound(obj.ViewObject)
    return obj


class Compound(base_aplanpythonobject.BaseAplanPythonObject):
    BaseType = "Aplan::CompoundPython"

    def __init__(self, obj):
        super(Compound, self).__init__(obj)
