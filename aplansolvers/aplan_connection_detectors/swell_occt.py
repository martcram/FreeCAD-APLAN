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

__title__ = ""
__author__ = "Martijn Cramer"
__url__ = "https://www.freecadweb.org"

from aplantools import aplanutils
try:
    import aplansolvers.aplan_connection_detectors.base_connection_detector as base
    import enum
except ImportError as ie:
    aplanutils.missingPythonModule(str(ie.name or ""))


class RefinementMethod(enum.Enum):
    None_ = ("None", "")
    BoundBox = ("BoundBox_Intersection", "Tooltip information about this refinement method")


class SolverMethod(enum.Enum):
    DistToShape   = ("BRepExtrema_DistShapeShape", "Tooltip information about this solver method")
    MeshInside    = ("BRepMesh_SolidClassifier",   "Tooltip information about this solver method")
    GeoDataInside = ("GeoData_SolidClassifier",    "Tooltip information about this solver method")
    Proximity     = ("BRepExtrema_ShapeProximity", "Tooltip information about this solver method")
    Section       = ("BRepAlgoAPI_Section",        "Tooltip information about this solver method")


def create(doc, name: str = "SwellOCCT"):
    return aplanutils.createObject(doc, name, SwellOCCT, VPSwellOCCT)


class SwellOCCT(base.IConnectionDetector):
    def __init__(self, obj):
        super(SwellOCCT, self).__init__(obj)
        obj.Proxy = self
        self.addProperties(obj)

    def addProperties(self, obj):
        if hasattr(obj, "Type"):
            obj.Type = self.__class__.__name__

        if not hasattr(obj, "RefinementMethod"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "RefinementMethod",
                "Connection detector",
                "..."
            )
            obj.RefinementMethod = [method.value[0] for method in RefinementMethod]

        if not hasattr(obj, "SwellDistance"):
            obj.addProperty(
                "App::PropertyFloat",
                "SwellDistance",
                "Connection detector",
                "..."
            )
            obj.SwellDistance = 0.01

        if not hasattr(obj, "SolverMethod"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "SolverMethod",
                "Connection detector",
                "..."
            )
            obj.SolverMethod = [method.value[0] for method in SolverMethod]
        
        if not hasattr(obj, "SampleRate"):
            obj.addProperty(
                "App::PropertyFloat",
                "SampleRate",
                "Connection detector",
                "..."
            )
            obj.SampleRate = 0.01

        if not hasattr(obj, "Tolerance"):
            obj.addProperty(
                "App::PropertyFloat",
                "Tolerance",
                "Connection detector",
                "..."
            )
            obj.Tolerance = 0.00001
        
        if not hasattr(obj, "MinDistance"):
            obj.addProperty(
                "App::PropertyFloat",
                "MinDistance",
                "Connection detector",
                "..."
            )
            obj.MinDistance = 0.00001


class VPSwellOCCT(base.IVPConnectionDetector):
    def setEdit(self, vobj, mode=0):
        return True

    def unsetEdit(self, vobj, mode=0):
        return True

    def doubleClicked(self, vobj):
        return True
