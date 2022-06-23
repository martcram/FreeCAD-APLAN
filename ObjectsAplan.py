# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2016 Bernd Hahnebach <bernd@bimstatik.org>              *
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

__title__ = "Objects APLAN"
__author__ = "Martijn Cramer, Bernd Hahnebach"
__url__ = "https://www.freecadweb.org"

# \addtogroup APLAN
#  @{

import FreeCAD
import typing


# ********* analysis objects ************************************************
def makeAnalysis(doc, name="Analysis"):
    """makeAnalysis(document, [name]):
    makes an APLAN analysis object"""
    obj = doc.addObject("Aplan::AplanAnalysis", name)
    return obj


# ********* constraint objects **********************************************
def makeCompound(analysis, components: typing.List, name="Compound"):
    """makeCompound(analysis, components, [name]):
    makes an APLAN Compound object"""
    import aplanobjects.compound
    obj = aplanobjects.compound.create(FreeCAD.ActiveDocument, analysis, components, name)
    return obj


def makeCompoundGroup(doc, name="Compounds"):
    """makeCompoundGroup(document, [name]):
    makes an APLAN compound group object"""
    obj = doc.addObject("Aplan::AplanCompoundGroup", name)
    return obj


def makePartFilter(doc, name="PartFilter"):
    """makePartFilter(document, [name]):
    makes an APLAN PartFilter object"""
    import aplanobjects.part_filter
    obj = aplanobjects.part_filter.create(doc, name)
    return obj


def makeTopoConstraints(doc, name="TopoConstraints"):
    """makeTopoConstraints(document, [name]):
    makes an APLAN TopoConstraints object"""
    import aplanobjects.topo_constraints
    obj = aplanobjects.topo_constraints.create(doc, name)
    return obj
